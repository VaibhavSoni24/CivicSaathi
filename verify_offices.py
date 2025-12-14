import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "municipal.settings")
django.setup()

from civic_saathi.models import Office

print(f'Total offices: {Office.objects.count()}')
print('\nOffices by city:')
for city in ['Jaipur', 'Delhi', 'Mumbai']:
    count = Office.objects.filter(city=city).count()
    print(f'  {city}: {count} offices')

print('\nSample offices:')
for office in Office.objects.all()[:5]:
    print(f'  - {office.name} (Dept: {office.department.name[:50]}...)')
