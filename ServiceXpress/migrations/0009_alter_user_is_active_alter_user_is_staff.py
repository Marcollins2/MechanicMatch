# Generated by Django 4.1.7 on 2024-11-11 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceXpress', '0008_alter_servicerequest_service_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=None),
        ),
    ]
