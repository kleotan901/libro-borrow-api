# Generated by Django 4.2.1 on 2024-09-18 08:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowing",
            name="fine_is_paid",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]