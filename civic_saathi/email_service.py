"""
Email Service for Municipal Governance System
Handles all email notifications for complaints, assignments, escalations, etc.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_complaint_registered_email(complaint):
    """Send email when a new complaint is registered"""
    try:
        subject = f"Complaint Registered - #{complaint.id}"
        
        # Email to citizen
        citizen_message = f"""
        Dear {complaint.user.first_name or complaint.user.username},
        
        Your complaint has been successfully registered.
        
        Complaint Details:
        - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
        - Title: {complaint.title}
        - Department: {complaint.department.name if complaint.department else 'Being assigned'}
        - Status: {complaint.get_status_display()}
        - Priority: {complaint.priority}
        
        Description:
        {complaint.description}
        
        You can track your complaint status through our portal.
        
        Thank you for helping improve our community!
        
        Municipal Governance Team
        """
        
        send_mail(
            subject,
            citizen_message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
            [complaint.user.email],
            fail_silently=True,
        )
        
        # Email to department officer if department assigned
        if complaint.department:
            officers = complaint.department.officer_set.all()
            if officers.exists():
                officer_emails = [officer.user.email for officer in officers if officer.user.email]
                if officer_emails:
                    officer_message = f"""
                    New complaint assigned to {complaint.department.name} department.
                    
                    Complaint Details:
                    - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
                    - Title: {complaint.title}
                    - Location: {complaint.location}
                    - Priority: {complaint.priority}
                    - Filed by: {complaint.user.get_full_name() or complaint.user.username}
                    
                    Please review and assign to appropriate worker.
                    
                    Login to admin panel: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/admin/
                    """
                    
                    send_mail(
                        f"New Complaint - {complaint.title}",
                        officer_message,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                        officer_emails,
                        fail_silently=True,
                    )
        
        return True
    except Exception as e:
        print(f"Error sending complaint registered email: {e}")
        return False


def send_worker_assignment_email(complaint, worker, officer):
    """Send email when a complaint is assigned to a worker"""
    try:
        if not worker or not worker.user.email:
            return False
        
        subject = f"New Task Assigned - Complaint #{complaint.id}"
        
        message = f"""
        Dear {worker.user.first_name or worker.user.username},
        
        A new complaint has been assigned to you by {officer.user.get_full_name() or officer.user.username}.
        
        Complaint Details:
        - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
        - Title: {complaint.title}
        - Location: {complaint.location}, {complaint.city}
        - Priority: {'High' if complaint.priority >= 2 else 'Normal'}
        - Status: {complaint.get_status_display()}
        
        Description:
        {complaint.description}
        
        Please login to the admin panel to view complete details and update the status.
        
        Admin Panel: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/admin/
        
        Thank you for your service!
        
        Municipal Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
            [worker.user.email],
            fail_silently=True,
        )
        
        return True
    except Exception as e:
        print(f"Error sending worker assignment email: {e}")
        return False


def send_status_update_email(complaint, old_status, new_status):
    """Send email when complaint status is updated"""
    try:
        if not complaint.user.email:
            return False
        
        subject = f"Complaint Status Updated - #{complaint.id}"
        
        message = f"""
        Dear {complaint.user.first_name or complaint.user.username},
        
        Your complaint status has been updated.
        
        Complaint Details:
        - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
        - Title: {complaint.title}
        - Previous Status: {old_status}
        - New Status: {new_status}
        
        """
        
        if new_status == 'RESOLVED' or new_status == 'COMPLETED':
            message += f"""
        Your complaint has been resolved. If the issue persists, please file a new complaint.
        
        We appreciate your patience and cooperation in helping us improve our services.
            """
        elif new_status == 'IN_PROGRESS':
            message += f"""
        Our team is actively working on resolving your complaint. You will be notified once it's completed.
            """
        
        message += """
        
        You can track your complaint status through our portal.
        
        Thank you!
        
        Municipal Governance Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
            [complaint.user.email],
            fail_silently=True,
        )
        
        return True
    except Exception as e:
        print(f"Error sending status update email: {e}")
        return False


def send_escalation_email(escalation):
    """Send email when a complaint is escalated"""
    try:
        complaint = escalation.complaint
        
        # Email to the officer receiving the escalation
        if escalation.escalated_to and escalation.escalated_to.user.email:
            subject = f"URGENT: Complaint Escalated - #{complaint.id}"
            
            message = f"""
            ESCALATION ALERT
            
            A complaint has been escalated to your attention.
            
            Complaint Details:
            - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
            - Title: {complaint.title}
            - Location: {complaint.location}, {complaint.city}
            - Priority: {complaint.priority}
            - Status: {complaint.get_status_display()}
            - Filed on: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}
            
            Escalation Details:
            - Reason: {escalation.reason}
            - Escalated by: {escalation.escalated_from.user.get_full_name() if escalation.escalated_from else 'System'}
            - Escalated at: {escalation.escalated_at.strftime('%Y-%m-%d %H:%M')}
            
            Previously assigned to:
            - Worker: {complaint.current_worker.user.get_full_name() if complaint.current_worker else 'Not assigned'}
            - Officer: {complaint.current_officer.user.get_full_name() if complaint.current_officer else 'Not assigned'}
            
            Description:
            {complaint.description}
            
            IMMEDIATE ACTION REQUIRED
            
            Please login to the admin panel and take appropriate action.
            
            Admin Panel: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/admin/
            
            Municipal Governance System
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                [escalation.escalated_to.user.email],
                fail_silently=True,
            )
        
        # Email to citizen about escalation
        if complaint.user.email:
            subject = f"Your Complaint Has Been Escalated - #{complaint.id}"
            
            citizen_message = f"""
            Dear {complaint.user.first_name or complaint.user.username},
            
            Your complaint has been escalated to senior authorities for priority handling.
            
            Complaint Details:
            - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
            - Title: {complaint.title}
            - Escalation Reason: {escalation.reason}
            
            We are committed to resolving your issue as quickly as possible. A senior officer is now overseeing your complaint.
            
            Thank you for your patience.
            
            Municipal Governance Team
            """
            
            send_mail(
                subject,
                citizen_message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                [complaint.user.email],
                fail_silently=True,
            )
        
        # Email to the worker who didn't complete the task (if applicable)
        if complaint.current_worker and complaint.current_worker.user.email:
            subject = f"Complaint Escalated - Performance Notice"
            
            worker_message = f"""
            Dear {complaint.current_worker.user.first_name or complaint.current_worker.user.username},
            
            A complaint assigned to you has been escalated due to delayed resolution.
            
            Complaint Details:
            - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
            - Title: {complaint.title}
            - Assigned on: {complaint.updated_at.strftime('%Y-%m-%d')}
            - Escalation Reason: {escalation.reason}
            
            Please note that timely resolution of assigned tasks is important for maintaining service quality.
            If you face any challenges in completing assignments, please communicate with your supervisor promptly.
            
            Municipal Administration
            """
            
            send_mail(
                subject,
                worker_message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                [complaint.current_worker.user.email],
                fail_silently=True,
            )
        
        return True
    except Exception as e:
        print(f"Error sending escalation email: {e}")
        return False


def send_sla_warning_email(complaint, hours_remaining):
    """Send warning email when complaint is approaching SLA deadline"""
    try:
        # Email to assigned worker
        if complaint.current_worker and complaint.current_worker.user.email:
            subject = f"SLA Warning - Complaint #{complaint.id} - {hours_remaining}h remaining"
            
            message = f"""
            SLA DEADLINE WARNING
            
            A complaint assigned to you is approaching its resolution deadline.
            
            Complaint Details:
            - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
            - Title: {complaint.title}
            - Location: {complaint.location}
            - Time Remaining: {hours_remaining} hours
            
            Please ensure timely completion to avoid escalation.
            
            Municipal Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                [complaint.current_worker.user.email],
                fail_silently=True,
            )
        
        # Email to supervising officer
        if complaint.current_officer and complaint.current_officer.user.email:
            subject = f"SLA Warning - Complaint #{complaint.id}"
            
            officer_message = f"""
            SLA DEADLINE WARNING
            
            A complaint under your supervision is approaching its resolution deadline.
            
            Complaint Details:
            - Tracking ID: CMP-{complaint.created_at.year}-{complaint.id:05d}
            - Title: {complaint.title}
            - Assigned to: {complaint.current_worker.user.get_full_name() if complaint.current_worker else 'Not assigned'}
            - Time Remaining: {hours_remaining} hours
            
            Please follow up with the assigned worker to ensure timely resolution.
            
            Municipal System
            """
            
            send_mail(
                subject,
                officer_message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@municipal.gov',
                [complaint.current_officer.user.email],
                fail_silently=True,
            )
        
        return True
    except Exception as e:
        print(f"Error sending SLA warning email: {e}")
        return False
