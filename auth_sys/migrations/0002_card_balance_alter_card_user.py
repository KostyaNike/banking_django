# Generated by Django 5.1.3 on 2024-12-28 21:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_sys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='card',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_cards', to=settings.AUTH_USER_MODEL),
        ),
    ]
