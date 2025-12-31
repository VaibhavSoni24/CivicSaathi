"""
Management command to create dummy complaints for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from civic_saathi.models import (
    Complaint, ComplaintCategory, CustomUser, Officer, Worker,
    Department, ComplaintLog
)
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Create dummy complaints for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of complaints to create (default: 50)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {count} dummy complaints...'))
        
        # Get all categories
        categories = list(ComplaintCategory.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No complaint categories found. Run setup_system.py first.'))
            return
        
        # Get or create test citizen users
        citizens = []
        for i in range(10):
            username = f'citizen{i+1}'
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'user_type': 'CITIZEN',
                    'city': fake.city(),
                    'state': fake.state(),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            citizens.append(user)
        
        # Get all officers and workers
        officers = list(Officer.objects.all())
        workers = list(Worker.objects.all())
        
        # Status distribution
        statuses = [
            ('SUBMITTED', 10),
            ('PENDING', 15),
            ('ASSIGNED', 10),
            ('IN_PROGRESS', 8),
            ('RESOLVED', 5),
            ('COMPLETED', 2),
        ]
        
        # Create complaints
        created_count = 0
        
        for i in range(count):
            # Select random data
            category = random.choice(categories)
            citizen = random.choice(citizens)
            
            # Determine status and age
            status_weights = [s[1] for s in statuses]
            status = random.choices([s[0] for s in statuses], weights=status_weights)[0]
            
            # Vary the creation time based on status
            if status in ['SUBMITTED', 'PENDING']:
                # Recent complaints
                hours_ago = random.randint(1, 48)
            elif status in ['ASSIGNED', 'IN_PROGRESS']:
                # Older complaints (some should exceed SLA)
                hours_ago = random.randint(6, 72)
            else:
                # Resolved/completed
                hours_ago = random.randint(24, 168)
            
            created_at = timezone.now() - timedelta(hours=hours_ago)
            
            # Select priority
            if hours_ago > 48:
                priority = random.choice([2, 3])  # Higher priority for older ones
            else:
                priority = random.choice([1, 1, 2])  # Mostly normal
            
            # Create complaint
            complaint = Complaint.objects.create(
                user=citizen,
                category=category,
                department=category.department,
                title=self._generate_title(category.name),
                description=self._generate_description(category.name),
                location=f"{fake.street_address()}, {fake.city()}",
                city=random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Hyderabad']),
                state=random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Telangana']),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                priority=priority,
                status=status,
                created_at=created_at,
                upvote_count=random.randint(0, 50),
                filter_passed=True,  # Demo complaints pass filter check
                filter_checked=True,  # Mark as already checked
            )
            
            # Assign officer and worker for non-submitted complaints
            if status != 'SUBMITTED' and officers:
                dept_officers = [o for o in officers if o.department == category.department]
                if dept_officers:
                    complaint.current_officer = random.choice(dept_officers)
                    
                    if status in ['ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'COMPLETED'] and workers:
                        dept_workers = [w for w in workers if w.department == category.department]
                        if dept_workers:
                            complaint.current_worker = random.choice(dept_workers)
            
            complaint.save()
            
            # Create initial log
            ComplaintLog.objects.create(
                complaint=complaint,
                action_by=citizen,
                note=f"Complaint filed by citizen",
                new_status='SUBMITTED',
                timestamp=created_at
            )
            
            # Create additional logs based on status
            if status != 'SUBMITTED':
                ComplaintLog.objects.create(
                    complaint=complaint,
                    action_by=complaint.current_officer.user if complaint.current_officer else None,
                    note=f"Status changed to {status}",
                    old_status='SUBMITTED',
                    new_status=status,
                    timestamp=created_at + timedelta(hours=random.randint(1, 4))
                )
            
            created_count += 1
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1}/{count} complaints...')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully created {created_count} dummy complaints!\n'
                f'  - Distributed across {len(categories)} categories\n'
                f'  - Created by {len(citizens)} test citizens\n'
                f'  - Various statuses and ages for testing'
            )
        )
        self.stdout.write('=' * 60)
        self.stdout.write('\nTo test escalation, some complaints are older than their SLA deadlines.')
        self.stdout.write('Run: python manage.py auto_escalate --dry-run')
    
    def _generate_title(self, category_name):
        """Generate realistic complaint title based on category"""
        templates = {
            'Pothole': [
                'Large pothole on {street}',
                'Dangerous pothole causing accidents',
                'Multiple potholes need repair',
                'Deep pothole damaging vehicles',
            ],
            'Garbage': [
                'Garbage not collected for days',
                'Overflowing garbage bins',
                'Illegal garbage dumping',
                'Garbage collection schedule issue',
            ],
            'Street Light': [
                'Street light not working since {days} days',
                'Multiple street lights out',
                'Broken street light pole',
                'Street light flickering',
            ],
            'Water': [
                'No water supply for {days} days',
                'Water leakage on road',
                'Contaminated water issue',
                'Low water pressure problem',
            ],
            'Drain': [
                'Blocked drain causing flooding',
                'Sewage overflow issue',
                'Manhole cover missing',
                'Drainage cleaning required',
            ],
        }
        
        # Find matching template
        for key in templates:
            if key.lower() in category_name.lower():
                template = random.choice(templates[key])
                return template.replace('{street}', fake.street_name()).replace('{days}', str(random.randint(2, 7)))
        
        # Default
        return f"{category_name} issue at {fake.street_name()}"
    
    def _generate_description(self, category_name):
        """Generate realistic description"""
        issues = [
            f"There is a serious {category_name.lower()} issue that needs immediate attention.",
            f"The {category_name.lower()} problem has been persisting for several days now.",
            f"Urgent action required for {category_name.lower()} in our area.",
            f"Multiple residents are affected by this {category_name.lower()} issue.",
            f"This {category_name.lower()} problem is causing inconvenience to the community.",
        ]
        
        impacts = [
            "It is causing major inconvenience to residents.",
            "Children and elderly are particularly affected.",
            "This poses a safety hazard.",
            "The situation is getting worse each day.",
            "Immediate action is required to prevent further problems.",
        ]
        
        return f"{random.choice(issues)} {random.choice(impacts)}"
