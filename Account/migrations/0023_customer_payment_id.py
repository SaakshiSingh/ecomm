# Generated by Django 3.2.9 on 2021-11-27 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0022_auto_20210813_0325'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
