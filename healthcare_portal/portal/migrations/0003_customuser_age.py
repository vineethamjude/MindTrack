# Generated by Django 4.2.5 on 2023-10-01 10:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0002_customuser_availability"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="age",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
