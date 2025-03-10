# Generated by Django 5.1.4 on 2025-03-09 13:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_banka_goal_alter_banka_hash_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='banka',
            name='hash_code',
            field=models.CharField(default='b9fbb160bfe3', max_length=12, unique=True),
        ),
        migrations.CreateModel(
            name='UserCashback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cafe_restaurants', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('kids_stores', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('e_scooters', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cinemas', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('transport', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('mobile_recharge', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('parking', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('max_cashback', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cashback', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
