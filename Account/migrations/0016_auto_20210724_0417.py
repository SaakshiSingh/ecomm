# Generated by Django 3.0.3 on 2021-07-23 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0015_auto_20210724_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='picture',
            field=models.ImageField(blank=True, default='images/default.png', null=True, upload_to='images'),
        ),
    ]
