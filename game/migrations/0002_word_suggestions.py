# Generated by Django 5.2.2 on 2025-06-06 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='suggestions',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
