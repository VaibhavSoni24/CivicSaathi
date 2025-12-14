# Generated manually to fix foreign key constraint for user field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0003_add_office_to_complaint'),
    ]

    operations = [
        # Drop the existing incorrect foreign key constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE civic_saathi_complaint 
                DROP CONSTRAINT IF EXISTS civic_saathi_complaint_user_id_fkey;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Add the correct foreign key constraint pointing to custom_user
        migrations.RunSQL(
            sql="""
                ALTER TABLE civic_saathi_complaint 
                ADD CONSTRAINT civic_saathi_complaint_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES custom_user(id) 
                ON DELETE CASCADE 
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE civic_saathi_complaint 
                DROP CONSTRAINT IF EXISTS civic_saathi_complaint_user_id_fkey;
            """,
        ),
    ]
