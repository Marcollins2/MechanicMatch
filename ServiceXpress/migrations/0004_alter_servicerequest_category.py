# Generated by Django 5.1.3 on 2024-11-10 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceXpress', '0003_user_user_type_alter_servicerequest_service_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='category',
            field=models.CharField(choices=[('washing', 'washing'), ('repair', 'repair'), ('maintenance', 'maintenance')], max_length=100),
        ),
    ]
