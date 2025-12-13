"""
Create all missing tables for the civic_saathi app
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal.settings')
django.setup()

from django.db import connection

# Create missing tables
print("Creating missing tables...")

with connection.cursor() as cursor:
    # Create SubAdminCategory table
    print("\n1. Creating SubAdminCategory table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_subadmincategory (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category_type VARCHAR(30) NOT NULL,
            description TEXT DEFAULT ''
        );
    """)
    print("✓ SubAdminCategory table created")
    
    # Now add the foreign key to Department table
    print("\n2. Adding sub_admin_category_id to Department table...")
    cursor.execute("""
        ALTER TABLE civic_saathi_department 
        ADD COLUMN IF NOT EXISTS sub_admin_category_id BIGINT 
        REFERENCES civic_saathi_subadmincategory(id) ON DELETE CASCADE;
    """)
    print("✓ Foreign key added to Department table")
    
    # Create other missing profile tables
    print("\n3. Creating AdminProfile table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_adminprofile (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL REFERENCES custom_user(id) ON DELETE CASCADE,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL
        );
    """)
    print("✓ AdminProfile table created")
    
    print("\n4. Creating SubAdminProfile table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_subadminprofile (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL REFERENCES custom_user(id) ON DELETE CASCADE,
            category_id BIGINT NOT NULL REFERENCES civic_saathi_subadmincategory(id) ON DELETE CASCADE,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL
        );
    """)
    print("✓ SubAdminProfile table created")
    
    print("\n5. Creating DepartmentAdminProfile table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_departmentadminprofile (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL REFERENCES custom_user(id) ON DELETE CASCADE,
            department_id BIGINT NOT NULL REFERENCES civic_saathi_department(id) ON DELETE CASCADE,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL
        );
    """)
    print("✓ DepartmentAdminProfile table created")
    
    print("\n6. Creating WorkerProfile table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_workerprofile (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL REFERENCES custom_user(id) ON DELETE CASCADE,
            department_id BIGINT NOT NULL REFERENCES civic_saathi_department(id) ON DELETE CASCADE,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL,
            skills TEXT DEFAULT ''
        );
    """)
    print("✓ WorkerProfile table created")
    
    print("\n7. Creating DepartmentAttendance table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_departmentattendance (
            id BIGSERIAL PRIMARY KEY,
            department_id BIGINT NOT NULL REFERENCES civic_saathi_department(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            present_count INTEGER DEFAULT 0,
            absent_count INTEGER DEFAULT 0,
            total_workers INTEGER DEFAULT 0,
            UNIQUE(department_id, date)
        );
    """)
    print("✓ DepartmentAttendance table created")
    
    print("\n8. Creating ComplaintVote table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS civic_saathi_complaintvote (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES custom_user(id) ON DELETE CASCADE,
            complaint_id BIGINT NOT NULL REFERENCES civic_saathi_complaint(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, complaint_id)
        );
    """)
    print("✓ ComplaintVote table created")

print("\n✅ All missing tables created successfully!")
