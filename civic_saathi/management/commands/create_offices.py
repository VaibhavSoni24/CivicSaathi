"""
Management command to create offices for all departments
Creates offices in Jaipur, Delhi, and Mumbai for each department
"""
from django.core.management.base import BaseCommand
from civic_saathi.models import Department, Office


class Command(BaseCommand):
    help = 'Create offices in Jaipur, Delhi, and Mumbai for all departments'

    def handle(self, *args, **kwargs):
        # Define the three cities with their state information
        cities = [
            {'name': 'Jaipur', 'state': 'Rajasthan'},
            {'name': 'Delhi', 'state': 'Delhi'},
            {'name': 'Mumbai', 'state': 'Maharashtra'},
        ]
        
        departments = Department.objects.all()
        
        if not departments.exists():
            self.stdout.write(self.style.ERROR('No departments found. Please run init_data command first.'))
            return
        
        created_count = 0
        existing_count = 0
        
        for department in departments:
            for city_info in cities:
                city_name = city_info['name']
                state_name = city_info['state']
                
                # Check if office already exists
                office, created = Office.objects.get_or_create(
                    department=department,
                    city=city_name,
                    defaults={
                        'name': f"{department.name} - {city_name} Office",
                        'state': state_name,
                        'address': f"{city_name}, {state_name}",
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {office.name}'
                        )
                    )
                else:
                    existing_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Already exists: {office.name}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Summary: {created_count} offices created, {existing_count} already existed'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Total offices: {Office.objects.count()}'
            )
        )
