"""
Django signals for automatic email notifications
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Complaint, ComplaintLog, Assignment, ComplaintEscalation
from .email_service import (
    send_complaint_registered_email,
    send_worker_assignment_email,
    send_status_update_email,
    send_escalation_email
)


@receiver(post_save, sender=Complaint)
def complaint_created_handler(sender, instance, created, **kwargs):
    """Send email when a new complaint is created"""
    if created:
        send_complaint_registered_email(instance)


@receiver(post_save, sender=Assignment)
def worker_assigned_handler(sender, instance, created, **kwargs):
    """Send email when a worker is assigned to a complaint"""
    if created and instance.assigned_to_worker:
        send_worker_assignment_email(
            instance.complaint,
            instance.assigned_to_worker,
            instance.assigned_by_officer
        )


@receiver(post_save, sender=ComplaintEscalation)
def escalation_created_handler(sender, instance, created, **kwargs):
    """Send email when a complaint is escalated"""
    if created:
        send_escalation_email(instance)


# Track status changes
_complaint_status_cache = {}

@receiver(pre_save, sender=Complaint)
def track_status_change(sender, instance, **kwargs):
    """Track the old status before save"""
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            _complaint_status_cache[instance.pk] = old_instance.status
        except Complaint.DoesNotExist:
            pass


@receiver(post_save, sender=Complaint)
def status_changed_handler(sender, instance, created, **kwargs):
    """Send email when complaint status changes"""
    if not created and instance.pk in _complaint_status_cache:
        old_status = _complaint_status_cache.get(instance.pk)
        new_status = instance.status
        
        if old_status != new_status:
            send_status_update_email(instance, old_status, new_status)
            
            # Create automatic log entry for status change
            ComplaintLog.objects.create(
                complaint=instance,
                action_by=None,  # System generated
                note=f"Status changed from {old_status} to {new_status}",
                old_status=old_status,
                new_status=new_status
            )
        
        # Clean up cache
        del _complaint_status_cache[instance.pk]
