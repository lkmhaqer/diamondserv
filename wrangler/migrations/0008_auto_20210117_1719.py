# Generated by Django 3.1.3 on 2021-01-17 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wrangler', '0007_servertype_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servertype',
            name='environment_vars',
            field=models.ManyToManyField(blank=True, to='wrangler.EnvironmentVar'),
        ),
    ]
