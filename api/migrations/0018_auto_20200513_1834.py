# Generated by Django 3.0.5 on 2020-05-13 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20200513_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='hand',
            field=models.CharField(blank=True, choices=[('', ''), ('hand', 'hand'), ('dessert', 'dessert')], default='', max_length=10),
        ),
    ]
