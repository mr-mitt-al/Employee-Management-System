# Generated by Django 5.1.1 on 2024-10-08 12:33

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_remove_requestleave_leave_requested_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestleave',
            name='leave_requested_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
