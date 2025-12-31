import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "municipal.settings")
django.setup()

from civic_saathi.models import Department, SubAdminCategory

# Load admin credentials to get department structure
with open('adminCredentials.json', 'r') as f:
    admin_creds = json.load(f)

# Create or get SubAdmin categories
clusters = {
    'CORE_CIVIC': 'Core Civic Departments',
    'MONITORING_COMPLIANCE': 'Monitoring & Compliance Departments',
    'ADMIN_WORKFORCE_TECH': 'Admin, Workforce & Tech',
    'SPECIAL_PROGRAM': 'Special Program Units'
}

sub_admin_categories = {}
for cluster_id, cluster_name in clusters.items():
    category, created = SubAdminCategory.objects.get_or_create(
        name=cluster_name,
        defaults={'category_type': cluster_id}
    )
    sub_admin_categories[cluster_id] = category
    if created:
        print(f"✅ Created SubAdminCategory: {cluster_name}")
    else:
        print(f"ℹ️  SubAdminCategory exists: {cluster_name}")

# Department mapping: adminCredentials departmentId -> database-friendly name
# These match what's in adminCredentials.json
department_mappings = [
    # Core Civic
    ("PWD_URBAN", "Roads & Infrastructure", "CORE_CIVIC"),
    ("SWM", "Sanitation & Waste Management", "CORE_CIVIC"),
    ("HEALTH", "Municipal Health", "CORE_CIVIC"),
    ("ELECTRICAL", "Electricity & Power", "CORE_CIVIC"),
    ("WATER", "Water Supply", "CORE_CIVIC"),
    ("DRAINAGE", "Drainage & Sewerage", "CORE_CIVIC"),
    # Monitoring & Compliance
    ("SANITATION", "Sanitation & Public Toilets", "MONITORING_COMPLIANCE"),
    ("VIGILANCE", "Vigilance & Enforcement", "MONITORING_COMPLIANCE"),
    ("ANIMAL", "Animal Control", "MONITORING_COMPLIANCE"),
    # Admin, Workforce & Tech
    ("HR", "Human Resources", "ADMIN_WORKFORCE_TECH"),
    ("IT", "IT & e-Governance", "ADMIN_WORKFORCE_TECH"),
    ("FINANCE", "Finance & Accounts", "ADMIN_WORKFORCE_TECH"),
    # Special Programs
    ("SBM_URBAN", "Swachh Bharat Mission", "SPECIAL_PROGRAM"),
    ("SMART_CITY", "Smart City Development", "SPECIAL_PROGRAM"),
]

print("\n📋 Creating/Updating Departments...")
created_count = 0
updated_count = 0

for dept_id, dept_name, category_key in department_mappings:
    category = sub_admin_categories[category_key]
    
    # Try to find existing department by similar name or create new
    dept, created = Department.objects.get_or_create(
        name=dept_name,
        defaults={
            'sub_admin_category': category,
            'description': f'{dept_name} - {clusters[category_key]}'
        }
    )
    
    if created:
        print(f"✅ Created: {dept_name} ({dept_id}) - {category_key}")
        created_count += 1
    else:
        # Update category if needed
        if dept.sub_admin_category != category:
            dept.sub_admin_category = category
            dept.save()
            print(f"🔄 Updated: {dept_name} category -> {category_key}")
            updated_count += 1
        else:
            print(f"ℹ️  Exists: {dept_name}")

print(f"\n📊 Summary:")
print(f"   Created: {created_count} departments")
print(f"   Updated: {updated_count} departments")
print(f"   Total departments now: {Department.objects.count()}")

# Show final department list
print("\n🏢 All Departments in Database:")
for dept in Department.objects.all().order_by('sub_admin_category__name', 'name'):
    print(f"   • {dept.name} ({dept.sub_admin_category.name})")
