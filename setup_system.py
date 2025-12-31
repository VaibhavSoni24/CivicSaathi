"""
Quick setup script to initialize the municipal governance system with
departments, categories, SLA configs, and test data.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal.settings')
django.setup()

from civic_saathi.models import (
    Department, ComplaintCategory, SLAConfig,
    SubAdminCategory, Officer, Worker, CustomUser
)
from django.contrib.auth.hashers import make_password
from datetime import date

def create_departments_and_categories():
    """Create departments and complaint categories with SLA configs"""
    
    print("=" * 70)
    print("MUNICIPAL GOVERNANCE SYSTEM - QUICK SETUP")
    print("=" * 70)
    print()
    
    # Create SubAdminCategories
    print("Creating Sub-Admin Categories...")
    core_civic, _ = SubAdminCategory.objects.get_or_create(
        name="Core Civic Services",
        category_type="CORE_CIVIC",
        defaults={'description': 'Core municipal services'}
    )
    
    monitoring, _ = SubAdminCategory.objects.get_or_create(
        name="Monitoring & Compliance",
        category_type="MONITORING_COMPLIANCE",
        defaults={'description': 'Monitoring and compliance services'}
    )
    
    print("✓ Sub-Admin Categories created")
    print()
    
    # Department and Category configurations
    dept_config = [
        {
            'name': 'Roads & Infrastructure',
            'sub_admin': core_civic,
            'description': 'Manages roads, bridges, and infrastructure',
            'categories': [
                {'name': 'Pothole', 'resolution': 24, 'escalation': 12},
                {'name': 'Road Damage', 'resolution': 48, 'escalation': 24},
                {'name': 'Bridge Issues', 'resolution': 72, 'escalation': 36},
                {'name': 'Footpath Repair', 'resolution': 72, 'escalation': 48},
            ]
        },
        {
            'name': 'Sanitation & Waste Management',
            'sub_admin': core_civic,
            'description': 'Handles garbage collection and sanitation',
            'categories': [
                {'name': 'Garbage Not Collected', 'resolution': 48, 'escalation': 24},
                {'name': 'Illegal Dumping', 'resolution': 24, 'escalation': 12},
                {'name': 'Overflowing Bin', 'resolution': 24, 'escalation': 12},
                {'name': 'Street Cleaning', 'resolution': 48, 'escalation': 24},
            ]
        },
        {
            'name': 'Electricity & Power',
            'sub_admin': core_civic,
            'description': 'Street lights and electrical infrastructure',
            'categories': [
                {'name': 'Street Light Not Working', 'resolution': 48, 'escalation': 24},
                {'name': 'Power Outage', 'resolution': 12, 'escalation': 6},
                {'name': 'Electrical Hazard', 'resolution': 6, 'escalation': 3},
                {'name': 'Transformer Issue', 'resolution': 24, 'escalation': 12},
            ]
        },
        {
            'name': 'Water Supply',
            'sub_admin': core_civic,
            'description': 'Water supply and distribution',
            'categories': [
                {'name': 'No Water Supply', 'resolution': 24, 'escalation': 12},
                {'name': 'Water Leakage', 'resolution': 48, 'escalation': 24},
                {'name': 'Contaminated Water', 'resolution': 12, 'escalation': 6},
                {'name': 'Low Water Pressure', 'resolution': 72, 'escalation': 36},
            ]
        },
        {
            'name': 'Drainage & Sewerage',
            'sub_admin': core_civic,
            'description': 'Drainage and sewerage systems',
            'categories': [
                {'name': 'Blocked Drain', 'resolution': 48, 'escalation': 24},
                {'name': 'Sewage Overflow', 'resolution': 12, 'escalation': 6},
                {'name': 'Manhole Cover Missing', 'resolution': 24, 'escalation': 12},
                {'name': 'Drainage Cleaning', 'resolution': 72, 'escalation': 48},
            ]
        },
        {
            'name': 'Traffic & Transport',
            'sub_admin': monitoring,
            'description': 'Traffic management and public transport',
            'categories': [
                {'name': 'Traffic Signal Not Working', 'resolution': 12, 'escalation': 6},
                {'name': 'Illegal Parking', 'resolution': 48, 'escalation': 24},
                {'name': 'Missing Traffic Sign', 'resolution': 72, 'escalation': 36},
                {'name': 'Bus Stop Damaged', 'resolution': 120, 'escalation': 72},
            ]
        },
        {
            'name': 'Parks & Recreation',
            'sub_admin': core_civic,
            'description': 'Public parks and recreational facilities',
            'categories': [
                {'name': 'Park Maintenance', 'resolution': 120, 'escalation': 72},
                {'name': 'Broken Equipment', 'resolution': 72, 'escalation': 48},
                {'name': 'Garden Cleaning', 'resolution': 72, 'escalation': 48},
                {'name': 'Damaged Benches', 'resolution': 120, 'escalation': 96},
            ]
        },
        {
            'name': 'Building Permissions',
            'sub_admin': monitoring,
            'description': 'Building plans and permissions',
            'categories': [
                {'name': 'Illegal Construction', 'resolution': 120, 'escalation': 72},
                {'name': 'Building Plan Approval', 'resolution': 240, 'escalation': 120},
                {'name': 'Encroachment', 'resolution': 72, 'escalation': 48},
            ]
        },
    ]
    
    print("Creating Departments and Categories with SLA Configurations...")
    print()
    
    created_depts = 0
    created_cats = 0
    created_slas = 0
    
    for dept_data in dept_config:
        # Create department
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={
                'sub_admin_category': dept_data['sub_admin'],
                'description': dept_data['description']
            }
        )
        
        if created:
            created_depts += 1
            print(f"✓ Created Department: {dept.name}")
        else:
            print(f"→ Department exists: {dept.name}")
        
        # Create categories for this department
        for cat_data in dept_data['categories']:
            category, created = ComplaintCategory.objects.get_or_create(
                name=cat_data['name'],
                department=dept
            )
            
            if created:
                created_cats += 1
                print(f"  ✓ Created Category: {cat_data['name']}")
            else:
                print(f"  → Category exists: {cat_data['name']}")
            
            # Create SLA config
            sla, created = SLAConfig.objects.get_or_create(
                category=category,
                defaults={
                    'resolution_hours': cat_data['resolution'],
                    'escalation_hours': cat_data['escalation']
                }
            )
            
            if created:
                created_slas += 1
                print(f"    ✓ SLA: Resolve in {cat_data['resolution']}h, Escalate after {cat_data['escalation']}h")
            else:
                print(f"    → SLA exists")
        
        print()
    
    print("=" * 70)
    print("SETUP SUMMARY")
    print("=" * 70)
    print(f"Created: {created_depts} departments")
    print(f"Created: {created_cats} complaint categories")
    print(f"Created: {created_slas} SLA configurations")
    print()
    
    print("✓ Setup Complete!")
    print()
    print("Next Steps:")
    print("1. Create officers and workers via admin panel")
    print("2. Set up email configuration in settings.py")
    print("3. Test email: python manage.py test_email your-email@example.com")
    print("4. Set up cron job for auto-escalation: python manage.py auto_escalate")
    print()
    print("Access admin panel at: http://localhost:8000/admin/")
    print("=" * 70)


if __name__ == '__main__':
    create_departments_and_categories()
