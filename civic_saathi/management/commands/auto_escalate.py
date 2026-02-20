"""
Management command to auto-escalate complaints that have exceeded their SLA
This command should be run periodically (e.g., every hour) via cron job or task scheduler
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from civic_saathi.models import Complaint, ComplaintEscalation, Officer, SLAConfig, ComplaintLog
from civic_saathi.email_service import send_escalation_email, send_sla_warning_email, send_overdue_email


class Command(BaseCommand):
    help = 'Auto-escalate complaints that have exceeded their SLA deadlines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be escalated without actually escalating',
        )
        parser.add_argument(
            '--warning-threshold',
            type=int,
            default=2,
            help='Hours before deadline to send warning (default: 2 hours)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        warning_threshold = options['warning_threshold']
        
        self.stdout.write(self.style.SUCCESS('Starting auto-escalation check...'))
        
        # Get all active complaints that are not yet resolved or completed
        active_complaints = Complaint.objects.filter(
            status__in=['SUBMITTED', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'SORTING'],
            is_deleted=False
        ).select_related('category', 'category__sla_config', 'current_worker', 'current_officer', 'department')
        
        escalated_count = 0
        warning_count = 0
        current_time = timezone.now()
        
        for complaint in active_complaints:
            # Skip if no category or no SLA config
            if not complaint.category or not hasattr(complaint.category, 'sla_config'):
                continue
            
            sla_config = complaint.category.sla_config
            escalation_deadline = complaint.created_at + timedelta(hours=sla_config.escalation_hours)
            warning_time = escalation_deadline - timedelta(hours=warning_threshold)
            
            hours_since_creation = (current_time - complaint.created_at).total_seconds() / 3600
            hours_until_deadline = (escalation_deadline - current_time).total_seconds() / 3600
            
            # Check if complaint should be escalated
            if current_time >= escalation_deadline:
                self.stdout.write(
                    self.style.WARNING(
                        f'Complaint #{complaint.id} has exceeded SLA deadline '
                        f'(created {hours_since_creation:.1f}h ago, deadline: {sla_config.escalation_hours}h)'
                    )
                )
                
                if not dry_run:
                    # Find a senior officer to escalate to
                    senior_officer = self._find_senior_officer(complaint)
                    
                    if senior_officer:
                        # Create escalation record
                        reason = (
                            f"Auto-escalation: SLA breach. Complaint not resolved within "
                            f"{sla_config.escalation_hours} hours. "
                        )
                        
                        if complaint.current_worker:
                            reason += f"Previously assigned to worker: {complaint.current_worker.user.get_full_name()}. "
                        
                        if complaint.current_officer:
                            reason += f"Supervised by: {complaint.current_officer.user.get_full_name()}."
                        else:
                            reason += "No officer was previously assigned."
                        
                        escalation = ComplaintEscalation.objects.create(
                            complaint=complaint,
                            escalated_from=complaint.current_officer,
                            escalated_to=senior_officer,
                            reason=reason
                        )
                        
                        # Update complaint status and priority
                        old_status = complaint.status
                        old_priority = complaint.priority
                        complaint.status = 'PENDING'  # Reset to pending for reassignment
                        complaint.priority = max(complaint.priority + 1, 3)  # Increase priority, max 3
                        complaint.save()
                        
                        # Create log entry
                        ComplaintLog.objects.create(
                            complaint=complaint,
                            action_by=None,  # System action
                            note=reason,
                            old_status=old_status,
                            new_status=complaint.status,
                        )
                        
                        # Send escalation emails (to officers/workers)
                        send_escalation_email(escalation)

                        # Notify citizen that their complaint was escalated due to SLA breach
                        send_overdue_email(complaint)
                        
                        escalated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Escalated to {senior_officer.user.get_full_name()}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Could not find senior officer for escalation'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'  [DRY RUN] Would escalate complaint #{complaint.id}'
                        )
                    )
                    escalated_count += 1
            
            # Check if warning should be sent
            elif current_time >= warning_time and hours_until_deadline > 0:
                self.stdout.write(
                    self.style.NOTICE(
                        f'Complaint #{complaint.id} approaching deadline '
                        f'({hours_until_deadline:.1f}h remaining)'
                    )
                )
                
                if not dry_run:
                    # Check if warning was already sent in the last hour
                    recent_warnings = ComplaintLog.objects.filter(
                        complaint=complaint,
                        note__icontains='SLA warning',
                        timestamp__gte=current_time - timedelta(hours=1)
                    )
                    
                    if not recent_warnings.exists():
                        send_sla_warning_email(complaint, int(hours_until_deadline))
                        
                        # Log the warning
                        ComplaintLog.objects.create(
                            complaint=complaint,
                            action_by=None,
                            note=f"SLA warning sent: {hours_until_deadline:.1f} hours remaining until escalation"
                        )
                        
                        warning_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Sent SLA warning'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'  [DRY RUN] Would send warning for complaint #{complaint.id}'
                        )
                    )
                    warning_count += 1
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE:\n'
                    f'  - Would escalate: {escalated_count} complaints\n'
                    f'  - Would warn: {warning_count} complaints'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'AUTO-ESCALATION COMPLETE:\n'
                    f'  - Escalated: {escalated_count} complaints\n'
                    f'  - Warnings sent: {warning_count} complaints'
                )
            )
        self.stdout.write('=' * 60)
    
    def _find_senior_officer(self, complaint):
        """
        Find a senior officer to escalate to.
        Logic: Find an officer in the same department who is not the current officer.
        If none found, find any officer in the department.
        """
        if not complaint.department:
            return None
        
        # Try to find a different officer in the same department
        officers = Officer.objects.filter(
            department=complaint.department
        ).exclude(
            id=complaint.current_officer.id if complaint.current_officer else None
        )
        
        if officers.exists():
            # Prefer officers with fewer assigned complaints (load balancing)
            return officers.annotate(
                complaint_count=models.Count('complaints')
            ).order_by('complaint_count').first()
        
        # If no other officer, return any officer in department
        return Officer.objects.filter(
            department=complaint.department
        ).first()


# Import models for the query
from django.db import models
