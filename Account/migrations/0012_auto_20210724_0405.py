# Generated by Django 3.0.3 on 2021-07-23 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0011_auto_20210723_0352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='picture',
            field=models.ImageField(default='images/default.png', upload_to='images/'),
        ),
    ]
