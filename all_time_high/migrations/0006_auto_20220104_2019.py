# Generated by Django 3.2.11 on 2022-01-04 20:19

from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('all_time_high', '0005_alltimehighrate_notify'),
    ]

    operations = [
        migrations.AddField(
            model_name='alltimehighrate',
            name='dropped_1_unit',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                  django.core.validators.MinValueValidator(Decimal('0.0'))],
                                      verbose_name='1 Birim Düşüş Kaydı'),
        ),
        migrations.AlterField(
            model_name='alltimehighrate',
            name='all_time_high_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                  django.core.validators.MinValueValidator(Decimal('0.0'))],
                                      verbose_name='Tüm Zamanların En Yüksek Kuru'),
        ),
        migrations.AlterField(
            model_name='alltimehighrate',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                  django.core.validators.MinValueValidator(Decimal('0.0'))],
                                      verbose_name='Güncel Kur'),
        ),
    ]
