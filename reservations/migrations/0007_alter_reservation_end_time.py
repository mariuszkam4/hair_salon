# Generated by Django 4.2.6 on 2023-11-06 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_service_specializations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
