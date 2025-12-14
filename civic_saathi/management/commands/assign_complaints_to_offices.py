"""
Management command to assign pending complaints to offices based on location
"""
from django.core.management import BaseCommand
from civic_saathi.models import Complaint, Office


class Command(BaseCommand):
    help = 'Assign pending complaints to offices based on city and department'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Assigning complaints to offices...'))
        
        # Get all complaints that are pending or approved and don't have an office
        complaints = Complaint.objects.filter(
            office__isnull=True,
            is_deleted=False
        ).exclude(
            status__in=['DECLINED', 'REJECTED', 'DELETED']
        )
        
        assigned_count = 0
        no_office_count = 0
        
        for complaint in complaints:
            if not complaint.department or not complaint.city:
                no_office_count += 1
                continue
            
            try:
                office = Office.objects.get(
                    department=complaint.department,
                    city__iexact=complaint.city,
                    is_active=True
                )
                complaint.office = office
                complaint.save()
                assigned_count += 1
                self.stdout.write(f'  ✓ Assigned complaint {complaint.id} to {office.name}')
            except Office.DoesNotExist:
                no_office_count += 1
                self.stdout.write(self.style.WARNING(f'  ✗ No office found for complaint {complaint.id} (city={complaint.city}, dept={complaint.department})'))
            except Office.MultipleObjectsReturned:
                office = Office.objects.filter(
                    department=complaint.department,
                    city__iexact=complaint.city,
                    is_active=True
                ).first()
                complaint.office = office
                complaint.save()
                assigned_count += 1
                self.stdout.write(f'  ✓ Assigned complaint {complaint.id} to {office.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Assignment complete!'))
        self.stdout.write(f'  Assigned: {assigned_count}')
        self.stdout.write(f'  No matching office: {no_office_count}')
        self.stdout.write(f'  Total processed: {assigned_count + no_office_count}')
