# Generated by Django 5.1.7 on 2025-03-29 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
    ]
