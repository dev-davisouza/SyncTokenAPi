# Generated by Django 5.1.5 on 2025-01-15 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_digitador'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='digitador',
            name='id',
        ),
        migrations.AddField(
            model_name='digitador',
            name='username',
            field=models.CharField(blank=True, max_length=15, primary_key=True, serialize=False, unique=True, verbose_name='username'),
        ),
    ]
