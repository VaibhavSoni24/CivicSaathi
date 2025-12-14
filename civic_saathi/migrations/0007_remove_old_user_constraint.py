# Generated manually to remove duplicate foreign key constraint
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0006_alter_customuser_options_alter_customuser_table'),
    ]

    operations = [
        # Drop the old foreign key constraint pointing to custom_user
        migrations.RunSQL(
            sql="""
                ALTER TABLE civic_saathi_complaint 
                DROP CONSTRAINT IF EXISTS civic_saathi_complaint_user_id_fkey;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
