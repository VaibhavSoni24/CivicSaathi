# Generated migration for SLA and escalation improvements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0002_office_complaint_office_worker_office'),
    ]

    operations = [
        # Add name field to Office with default
        migrations.AddField(
            model_name='office',
            name='name',
            field=models.CharField(default='Municipal Office', max_length=200),
            preserve_default=False,
        ),
        # Add missing fields to Office
        migrations.AddField(
            model_name='office',
            name='pincode',
            field=models.CharField(default='000000', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='office',
            name='office_hours',
            field=models.CharField(default='9:00 AM - 5:00 PM', max_length=100),
        ),
        migrations.AddField(
            model_name='office',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='office',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Modify Office fields
        migrations.AlterField(
            model_name='office',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='office',
            name='phone',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='office',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        # Add SLAConfig model
        migrations.CreateModel(
            name='SLAConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resolution_hours', models.PositiveIntegerField(default=48, help_text='Expected hours to resolve this type of complaint')),
                ('escalation_hours', models.PositiveIntegerField(default=24, help_text='Hours before auto-escalation if not resolved')),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sla_config', to='civic_saathi.complaintcategory')),
            ],
            options={
                'verbose_name': 'SLA Configuration',
                'verbose_name_plural': 'SLA Configurations',
            },
        ),
        # Update ComplaintEscalation to add related_name
        migrations.AlterField(
            model_name='complaintescalation',
            name='complaint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escalations', to='civic_saathi.complaint'),
        ),
    ]
