# Generated manually to create civic_saathi_customuser from auth_user
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0007_remove_old_user_constraint'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Create civic_saathi_customuser as a view or copy from auth_user
                DO $$
                BEGIN
                    -- If civic_saathi_customuser doesn't exist, create it from auth_user
                    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='civic_saathi_customuser') THEN
                        CREATE TABLE civic_saathi_customuser AS SELECT * FROM auth_user;
                        -- Add primary key
                        ALTER TABLE civic_saathi_customuser ADD PRIMARY KEY (id);
                        -- Add sequence
                        CREATE SEQUENCE IF NOT EXISTS civic_saathi_customuser_id_seq;
                        ALTER TABLE civic_saathi_customuser ALTER COLUMN id SET DEFAULT nextval('civic_saathi_customuser_id_seq');
                        PERFORM setval('civic_saathi_customuser_id_seq', (SELECT MAX(id) FROM civic_saathi_customuser));
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS civic_saathi_customuser CASCADE;
            """,
        ),
    ]
