# Generated manually to add office field to complaint
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('civic_saathi', '0002_office_complaint_office'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints', to='civic_saathi.office'),
        ),
    ]
