# Generated by Django 2.2.13 on 2020-12-04 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("humans", "0012_remove_user_server_signed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="last name"
            ),
        ),
    ]
