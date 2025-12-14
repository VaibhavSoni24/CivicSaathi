# Generated manually to migrate from custom_user to auth_user table
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0004_fix_user_foreign_key'),
    ]

    operations = [
        # Copy all data from custom_user to auth_user if it doesn't already exist
        migrations.RunSQL(
            sql="""
                -- First, ensure auth_user table exists with all the custom fields
                DO $$
                BEGIN
                    -- Add custom fields to auth_user if they don't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='auth_user' AND column_name='user_type') THEN
                        ALTER TABLE auth_user ADD COLUMN user_type VARCHAR(20) DEFAULT 'CITIZEN';
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='auth_user' AND column_name='phone') THEN
                        ALTER TABLE auth_user ADD COLUMN phone VARCHAR(15) DEFAULT '';
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='auth_user' AND column_name='city') THEN
                        ALTER TABLE auth_user ADD COLUMN city VARCHAR(100) DEFAULT '';
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='auth_user' AND column_name='state') THEN
                        ALTER TABLE auth_user ADD COLUMN state VARCHAR(100) DEFAULT '';
                    END IF;
                END $$;
                
                -- Copy data from custom_user to auth_user (only if custom_user exists and has different data)
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='custom_user') THEN
                        -- Insert users from custom_user that don't exist in auth_user
                        INSERT INTO auth_user (
                            id, password, last_login, is_superuser, username, first_name, 
                            last_name, email, is_staff, is_active, date_joined,
                            user_type, phone, city, state
                        )
                        SELECT 
                            id, password, last_login, is_superuser, username, first_name,
                            last_name, email, is_staff, is_active, date_joined,
                            user_type, phone, city, state
                        FROM custom_user
                        WHERE id NOT IN (SELECT id FROM auth_user)
                        ON CONFLICT (id) DO NOTHING;
                        
                        -- Update the sequence to the max id
                        PERFORM setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
