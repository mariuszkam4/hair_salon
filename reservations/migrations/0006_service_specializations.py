# Generated by Django 4.2.6 on 2023-11-05 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_alter_reservation_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='specializations',
            field=models.ManyToManyField(related_name='services', to='reservations.specializationchoice', verbose_name='specializations'),
        ),
    ]
