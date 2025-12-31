"""
Management command to create default SLA configurations for complaint categories
"""
from django.core.management.base import BaseCommand
from civic_saathi.models import ComplaintCategory, SLAConfig


class Command(BaseCommand):
    help = 'Create default SLA configurations for complaint categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default SLA configurations...'))
        
        # Default SLA values based on complaint type priority
        sla_defaults = {
            # Critical infrastructure (shorter SLAs)
            'pothole': {'resolution': 24, 'escalation': 12},
            'streetlight': {'resolution': 48, 'escalation': 24},
            'water': {'resolution': 24, 'escalation': 12},
            'electricity': {'resolution': 24, 'escalation': 12},
            'traffic': {'resolution': 48, 'escalation': 24},
            
            # Regular services
            'garbage': {'resolution': 48, 'escalation': 24},
            'sanitation': {'resolution': 72, 'escalation': 36},
            'drainage': {'resolution': 72, 'escalation': 36},
            'park': {'resolution': 120, 'escalation': 72},
            'building': {'resolution': 120, 'escalation': 72},
            
            # Default for others
            'default': {'resolution': 72, 'escalation': 48},
        }
        
        created_count = 0
        updated_count = 0
        
        for category in ComplaintCategory.objects.all():
            # Determine SLA based on category name
            category_name_lower = category.name.lower()
            sla_values = sla_defaults.get('default', {'resolution': 72, 'escalation': 48})
            
            for keyword, values in sla_defaults.items():
                if keyword in category_name_lower:
                    sla_values = values
                    break
            
            # Create or update SLA config
            sla_config, created = SLAConfig.objects.get_or_create(
                category=category,
                defaults={
                    'resolution_hours': sla_values['resolution'],
                    'escalation_hours': sla_values['escalation']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Created SLA for {category.name}: '
                        f'Resolution={sla_values["resolution"]}h, '
                        f'Escalation={sla_values["escalation"]}h'
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.NOTICE(
                        f'  → SLA already exists for {category.name}'
                    )
                )
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'SLA Configuration Complete:\n'
                f'  - Created: {created_count} new configurations\n'
                f'  - Existing: {updated_count} configurations'
            )
        )
        self.stdout.write('=' * 60)
        
        if created_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    '\nNote: You can customize SLA values in the admin panel at:\n'
                    'Admin > Civic Saathi > SLA Configurations'
                )
            )
