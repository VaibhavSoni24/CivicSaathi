"""
Management command to backdate complaints for testing escalation
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from civic_saathi.models import Complaint, ComplaintLog
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Backdate existing complaints to test SLA escalation'

    def handle(self, *args, **options):
        complaints = Complaint.objects.all()
        
        self.stdout.write("Backdating complaints for SLA testing...")
        self.stdout.write("=" * 60)
        
        updated_count = 0
        
        for complaint in complaints:
            # Assign different age brackets based on status
            if complaint.status == 'SUBMITTED':
                # 20% very old (overdue)
                if random.random() < 0.2:
                    hours_ago = random.randint(48, 168)  # 2-7 days
                else:
                    hours_ago = random.randint(1, 8)  # Recent
                    
            elif complaint.status == 'PENDING':
                # 40% overdue
                if random.random() < 0.4:
                    hours_ago = random.randint(24, 72)
                else:
                    hours_ago = random.randint(2, 12)
                    
            elif complaint.status == 'ASSIGNED':
                # 30% overdue
                if random.random() < 0.3:
                    hours_ago = random.randint(36, 120)
                else:
                    hours_ago = random.randint(6, 24)
                    
            elif complaint.status == 'IN_PROGRESS':
                # 50% overdue (testing escalation heavily)
                if random.random() < 0.5:
                    hours_ago = random.randint(48, 168)
                else:
                    hours_ago = random.randint(12, 48)
                    
            elif complaint.status == 'RESOLVED':
                hours_ago = random.randint(72, 240)
                
            elif complaint.status == 'COMPLETED':
                hours_ago = random.randint(120, 360)
                
            else:
                hours_ago = random.randint(1, 24)
            
            new_created_at = timezone.now() - timedelta(hours=hours_ago)
            
            # Update using QuerySet.update() to bypass auto_now_add
            Complaint.objects.filter(pk=complaint.pk).update(
                created_at=new_created_at
            )
            
            # Update complaint logs too
            ComplaintLog.objects.filter(complaint=complaint).update(
                timestamp=new_created_at
            )
            
            updated_count += 1
            
            if hours_ago > 24:
                self.stdout.write(self.style.WARNING(
                    f"  CMP-{complaint.id:05d}: Set to {hours_ago}h ago (likely overdue)"
                ))
            else:
                self.stdout.write(
                    f"  CMP-{complaint.id:05d}: Set to {hours_ago}h ago"
                )
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(
            f'✓ Successfully backdated {updated_count} complaints'
        ))
        self.stdout.write("=" * 60)
        self.stdout.write("\nNow run: python manage.py check_sla")
        self.stdout.write("Then run: python manage.py auto_escalate --dry-run")
