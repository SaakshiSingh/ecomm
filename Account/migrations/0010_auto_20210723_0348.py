# Generated by Django 3.0.3 on 2021-07-22 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0009_auto_20210722_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='picture',
            field=models.ImageField(blank=True, default='images/images/default.png', null=True, upload_to='images/'),
        ),
    ]
