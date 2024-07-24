# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-19 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ("humans", "0008_auto_20160903_1850"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(
                default="en-us", max_length=5, verbose_name="Prefered language"
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="body",
            field=models.TextField(verbose_name="Body"),
        ),
        migrations.AlterField(
            model_name="notification",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
        ),
        migrations.AlterField(
            model_name="notification",
            name="send_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="auth.Group",
                verbose_name="Send to",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="sent_at",
            field=models.DateTimeField(null=True, verbose_name="Sent at"),
        ),
        migrations.AlterField(
            model_name="notification",
            name="subject",
            field=models.CharField(max_length=150, verbose_name="Subject"),
        ),
        migrations.AlterField(
            model_name="notification",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Updated at"),
        ),
        migrations.AlterField(
            model_name="user",
            name="fingerprint",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Fingerprint"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="keyserver_url",
            field=models.URLField(blank=True, null=True, verbose_name="Key server URL"),
        ),
        migrations.AlterField(
            model_name="user",
            name="organization",
            field=models.CharField(
                blank=True, max_length=80, null=True, verbose_name="Organization"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="public_key",
            field=models.TextField(blank=True, null=True, verbose_name="Public key"),
        ),
        migrations.AlterField(
            model_name="user",
            name="server_signed",
            field=models.BooleanField(default=False, verbose_name="Server signed"),
        ),
        migrations.AlterField(
            model_name="user",
            name="timezone",
            field=timezone_field.fields.TimeZoneField(
                default="UTC", verbose_name="Timezone"
            ),
        ),
    ]
