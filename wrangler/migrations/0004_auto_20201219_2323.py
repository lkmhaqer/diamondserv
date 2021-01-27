# Generated by Django 3.1.3 on 2020-12-19 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wrangler', '0003_auto_20201217_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='servertype',
            name='version',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='servertype',
            unique_together={('name', 'version')},
        ),
    ]
