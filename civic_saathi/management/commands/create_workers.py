"""
Management command to create 3 workers for each office (126 total workers)
"""
from django.core.management import BaseCommand
from civic_saathi.models import Office, Worker, CustomUser
from django.db import connection
from datetime import date


class Command(BaseCommand):
    help = 'Create 3 workers for each of the 42 offices (126 total workers)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating workers...'))
        
        offices = Office.objects.filter(is_active=True).select_related('department')
        
        if not offices.exists():
            self.stdout.write(self.style.ERROR('No offices found. Please run create_offices first.'))
            return
        
        self.stdout.write(f'Found {offices.count()} offices')
        
        created_count = 0
        existing_count = 0
        
        worker_roles = ['Field Worker', 'Senior Worker', 'Supervisor']
        
        for office in offices:
            for i, role in enumerate(worker_roles, 1):
                # Create username
                dept_short = ''.join([word[0] for word in office.department.name.split()[:3]]).lower()
                city_short = office.city[:3].lower()
                username = f'{dept_short}_{city_short}_w{i}'
                
                # Check if user exists
                if CustomUser.objects.filter(username=username).exists():
                    existing_count += 1
                    continue
                
                # Create user in custom_user table first
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f'{username}@municipal.gov.in',
                    password='worker123',  # Default password
                    first_name=f'{role.split()[0]}',
                    last_name=f'{i} {office.department.name.split()[0][:15]}',
                    user_type='WORKER',
                    city=office.city,
                    state=office.state
                )
                
                # Now create the same user in auth_user table for Worker FK
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, 
                                          last_name, email, is_staff, is_active, date_joined)
                    SELECT id, password, last_login, is_superuser, username, first_name,
                           last_name, email, is_staff, is_active, date_joined
                    FROM custom_user WHERE id = %s
                """, [user.id])
                
                # Create worker (without office FK due to DB schema mismatch)
                worker = Worker.objects.create(
                    user_id=user.id,
                    department=office.department,
                    role=role,
                    address=office.address,
                    joining_date=date.today(),
                    is_active=True
                )
                
                created_count += 1
                self.stdout.write(f'  ✓ Created: {worker.user.username} - {worker.role} at {office.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Worker creation complete!'))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Already existed: {existing_count}')
        self.stdout.write(f'  Total: {created_count + existing_count}')
