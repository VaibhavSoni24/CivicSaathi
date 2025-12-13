"""
Data initialization script for Civic Saathi
Creates departments, categories, and sample data
"""
from django.core.management import BaseCommand
from civic_saathi.models import (
    CustomUser, SubAdminCategory, Department, ComplaintCategory,
    AdminProfile, SubAdminProfile, DepartmentAdminProfile
)
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Initialize departments, categories and admin accounts'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting initialization...'))
        
        # Create Sub-Admin Categories
        self.create_sub_admin_categories()
        
        # Create Departments
        self.create_departments()
        
        # Create Complaint Categories
        self.create_complaint_categories()
        
        self.stdout.write(self.style.SUCCESS('✓ Initialization complete!'))
    
    def create_sub_admin_categories(self):
        self.stdout.write('Creating Sub-Admin Categories...')
        
        categories = [
            {
                'name': 'Core Civic Departments',
                'category_type': 'CORE_CIVIC',
                'description': 'Essential infrastructure and public works departments'
            },
            {
                'name': 'Monitoring & Compliance Departments',
                'category_type': 'MONITORING_COMPLIANCE',
                'description': 'Departments for monitoring, enforcement and compliance'
            },
            {
                'name': 'Admin, Workforce & Tech',
                'category_type': 'ADMIN_WORKFORCE_TECH',
                'description': 'Administrative, HR and technology support departments'
            },
            {
                'name': 'Special Program Units',
                'category_type': 'SPECIAL_PROGRAMS',
                'description': 'Government special program implementation units'
            },
        ]
        
        for cat_data in categories:
            cat, created = SubAdminCategory.objects.get_or_create(
                category_type=cat_data['category_type'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✓ Created: {cat.name}')
    
    def create_departments(self):
        self.stdout.write('Creating Departments...')
        
        # Get categories
        core_civic = SubAdminCategory.objects.get(category_type='CORE_CIVIC')
        monitoring = SubAdminCategory.objects.get(category_type='MONITORING_COMPLIANCE')
        admin_tech = SubAdminCategory.objects.get(category_type='ADMIN_WORKFORCE_TECH')
        special = SubAdminCategory.objects.get(category_type='SPECIAL_PROGRAMS')
        
        departments = [
            # Core Civic
            {'name': 'Engineering / Public Works Department (PWD – Urban)', 'category': core_civic},
            {'name': 'Solid Waste Management (SWM) Department', 'category': core_civic},
            {'name': 'Health Department (Municipal)', 'category': core_civic},
            {'name': 'Electrical / Street Lighting Department', 'category': core_civic},
            {'name': 'Water Supply & Sewerage Department', 'category': core_civic},
            {'name': 'Drainage / Storm Water Department', 'category': core_civic},
            
            # Monitoring & Compliance
            {'name': 'Sanitation & Public Toilet Department', 'category': monitoring},
            {'name': 'Municipal Enforcement / Vigilance Department', 'category': monitoring},
            {'name': 'Animal Husbandry / Cattle Nuisance Department', 'category': monitoring},
            
            # Admin, Workforce & Tech
            {'name': 'Municipal HR / Establishment Department', 'category': admin_tech},
            {'name': 'IT / e-Governance Department', 'category': admin_tech},
            {'name': 'Finance & Accounts Department', 'category': admin_tech},
            
            # Special Programs
            {'name': 'Swachh Bharat Mission (Urban)', 'category': special},
            {'name': 'Smart City SPV', 'category': special},
        ]
        
        for dept_data in departments:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'sub_admin_category': dept_data['category']}
            )
            if created:
                self.stdout.write(f'  ✓ Created: {dept.name}')
    
    def create_complaint_categories(self):
        self.stdout.write('Creating Complaint Categories...')
        
        # Get departments
        pwd = Department.objects.get(name__icontains='Public Works')
        swm = Department.objects.get(name__icontains='Solid Waste')
        health = Department.objects.get(name__icontains='Health')
        electrical = Department.objects.get(name__icontains='Electrical')
        water = Department.objects.get(name__icontains='Water Supply')
        drainage = Department.objects.get(name__icontains='Drainage')
        sanitation = Department.objects.get(name__icontains='Sanitation')
        enforcement = Department.objects.get(name__icontains='Enforcement')
        animal = Department.objects.get(name__icontains='Animal')
        
        categories = [
            # PWD
            {'name': 'Pothole / Road Damage', 'department': pwd},
            {'name': 'Broken Pavement', 'department': pwd},
            {'name': 'Road Construction Issues', 'department': pwd},
            
            # SWM
            {'name': 'Garbage Not Collected', 'department': swm},
            {'name': 'Overflowing Dustbin', 'department': swm},
            {'name': 'Illegal Dumping', 'department': swm},
            
            # Electrical
            {'name': 'Street Light Not Working', 'department': electrical},
            {'name': 'Damaged Street Light', 'department': electrical},
            
            # Water Supply
            {'name': 'Water Supply Problem', 'department': water},
            {'name': 'Water Pipe Leakage', 'department': water},
            {'name': 'No Water Supply', 'department': water},
            
            # Drainage
            {'name': 'Drainage Blockage', 'department': drainage},
            {'name': 'Sewage Overflow', 'department': drainage},
            {'name': 'Manhole Cover Missing', 'department': drainage},
            
            # Sanitation
            {'name': 'Public Toilet Not Clean', 'department': sanitation},
            {'name': 'Public Toilet Not Working', 'department': sanitation},
            
            # Animal
            {'name': 'Stray Dogs', 'department': animal},
            {'name': 'Cattle Nuisance', 'department': animal},
            
            # Health
            {'name': 'Mosquito Breeding', 'department': health},
            {'name': 'Health Hazard', 'department': health},
            
            # Enforcement
            {'name': 'Illegal Construction', 'department': enforcement},
            {'name': 'Encroachment', 'department': enforcement},
        ]
        
        for cat_data in categories:
            cat, created = ComplaintCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'department': cat_data['department']}
            )
            if created:
                self.stdout.write(f'  ✓ Created: {cat.name}')
