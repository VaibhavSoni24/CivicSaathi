"""
Management command to create offices for all departments in specified cities
"""
from django.core.management import BaseCommand
from civic_saathi.models import Department, Office


class Command(BaseCommand):
    help = 'Create offices for all 14 departments in Jaipur, Delhi, and Mumbai'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating offices...'))
        
        cities = [
            {'name': 'Jaipur', 'state': 'Rajasthan'},
            {'name': 'Delhi', 'state': 'Delhi'},
            {'name': 'Mumbai', 'state': 'Maharashtra'},
        ]
        
        # Get only the main 14 departments (as per init_data.py)
        main_dept_keywords = [
            'Public Works',
            'Solid Waste Management',
            'Health Department',
            'Electrical',
            'Water Supply',
            'Drainage',
            'Sanitation',
            'Enforcement',
            'Animal',
            'HR',
            'e-Governance',  # Changed from 'IT' to match full name
            'Finance',
            'Swachh Bharat',
            'Smart City'
        ]
        
        departments = []
        for keyword in main_dept_keywords:
            dept = Department.objects.filter(name__icontains=keyword).first()
            if dept and dept not in departments:
                departments.append(dept)
        
        if not departments:
            self.stdout.write(self.style.ERROR('No departments found. Please run init_data first.'))
            return
        
        self.stdout.write(f'Found {len(departments)} main departments')
        
        created_count = 0
        existing_count = 0
        
        for city_data in cities:
            city = city_data['name']
            state = city_data['state']
            
            for department in departments:
                # Create a shorter name for the office
                dept_short_name = department.name.split('(')[0].strip()
                if len(dept_short_name) > 50:
                    dept_short_name = dept_short_name[:50]
                
                office, created = Office.objects.get_or_create(
                    department=department,
                    city=city,
                    defaults={
                        'name': f'{dept_short_name} Office - {city}',
                        'state': state,
                        'address': f'{dept_short_name} Office, Municipal Corporation, {city}, {state}',
                        'pincode': '000000',
                        'phone': '1800-000-0000',
                        'email': f'{department.name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")}_{city.lower()}@municipal.gov.in',
                        'office_hours': '9:00 AM - 5:00 PM',
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {office}')
                else:
                    existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Office creation complete!'))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Already existed: {existing_count}')
        self.stdout.write(f'  Total: {created_count + existing_count}')
