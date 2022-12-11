# Generated by Django 3.2.11 on 2022-01-04 20:59

from decimal import Decimal

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


# noinspection PyPep8Naming
def migrate_data_from_model_to_be_deleted(apps, schema_editor):
    AllTimeHighRate = apps.get_model("all_time_high", "AllTimeHighRate")
    AllTimeHigh = apps.get_model("all_time_high", "AllTimeHigh")
    ExchangeCurrency = apps.get_model("all_time_high", "ExchangeCurrency")
    ExchangeRate = apps.get_model("all_time_high", "ExchangeRate")

    all_time_high_rate = AllTimeHighRate.objects.last()

    if all_time_high_rate is not None:
        currency, created = ExchangeCurrency.objects.get_or_create(
            base=all_time_high_rate.currency_1, target=all_time_high_rate.currency_2
        )
        try:
            ExchangeRate.objects.get(currency=currency)
        except ExchangeRate.DoesNotExist:
            ExchangeRate.objects.create(
                currency=currency,
                exchange_rate=all_time_high_rate.exchange_rate
            )

        try:
            AllTimeHigh.objects.get(currency=currency)
        except AllTimeHigh.DoesNotExist:
            AllTimeHigh.objects.create(
                currency=currency,
                exchange_rate=all_time_high_rate.all_time_high_rate
            )


class Migration(migrations.Migration):
    dependencies = [
        ('all_time_high', '0006_auto_20220104_2019'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllTimeHigh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                                  django.core.validators.MinValueValidator(
                                                                      Decimal('0.0'))],
                                                      verbose_name='Tüm Zamanların En Yüksek Kuru')),
                ('notify', models.BooleanField(default=False, verbose_name='Bildir')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeCurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base', models.CharField(
                    max_length=3,
                    validators=[django.core.validators.MaxLengthValidator(3),
                                django.core.validators.MinLengthValidator(3),
                                django.core.validators.ProhibitNullCharactersValidator()],
                    verbose_name='Para Birimi 1')),
                ('target', models.CharField(
                    max_length=3,
                    validators=[django.core.validators.MaxLengthValidator(3),
                                django.core.validators.MinLengthValidator(3),
                                django.core.validators.ProhibitNullCharactersValidator()],
                    verbose_name='Para Birimi 2')),
            ],
        ),
        migrations.RemoveField(
            model_name='alltimehighrate',
            name='dropped_1_unit',
        ),
        migrations.AlterField(
            model_name='alltimehighrate',
            name='all_time_high_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True,
                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                  django.core.validators.MinValueValidator(Decimal('0.0'))],
                                      verbose_name='Tüm Zamanların En Yüksek Kuru'),
        ),
        migrations.AlterField(
            model_name='alltimehighrate',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True,
                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                  django.core.validators.MinValueValidator(Decimal('0.0'))],
                                      verbose_name='Güncel Kur'),
        ),
        migrations.CreateModel(
            name='OneUnitDropped',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                                  django.core.validators.MinValueValidator(
                                                                      Decimal('0.0'))],
                                                      verbose_name='1 Birim Düşüş Kaydı')),
                ('currency',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='all_time_high.exchangecurrency',
                                      verbose_name='Kur Birimleri')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10,
                                                      validators=[django.core.validators.DecimalValidator(10, 2),
                                                                  django.core.validators.MinValueValidator(
                                                                      Decimal('0.0'))], verbose_name='Güncel Kur')),
                ('record_date', models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')),
                ('currency',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='all_time_high.exchangecurrency',
                                   verbose_name='Kur Birimleri')),
            ],
        ),
        migrations.AddIndex(
            model_name='exchangecurrency',
            index=models.Index(fields=['base', 'target'], name='all_time_hi_base_400ef8_idx'),
        ),
        migrations.AddConstraint(
            model_name='exchangecurrency',
            constraint=models.UniqueConstraint(fields=('base', 'target'), name='unique_exchange_currencies'),
        ),
        migrations.AddField(
            model_name='alltimehigh',
            name='currency',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='all_time_high.exchangecurrency',
                                       verbose_name='Kur Birimleri'),
        ),
        migrations.AddField(
            model_name='alltimehigh',
            name='update_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi'),
        ),
        migrations.AddField(
            model_name='oneunitdropped',
            name='notify',
            field=models.BooleanField(default=False, verbose_name='Bildir'),
        ),
        migrations.AddField(
            model_name='oneunitdropped',
            name='update_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi'),
        ),
        migrations.AddIndex(
            model_name='exchangerate',
            index=models.Index(fields=['currency'], name='all_time_hi_currenc_617a39_idx'),
        ),
        migrations.AddIndex(
            model_name='exchangerate',
            index=models.Index(fields=['record_date'], name='all_time_hi_record__977606_idx'),
        ),
        migrations.AddConstraint(
            model_name='exchangerate',
            constraint=models.UniqueConstraint(fields=('exchange_rate', 'record_date'), name='unique_exchange_rate'),
        ),
        migrations.RunPython(
            migrate_data_from_model_to_be_deleted,
            reverse_code=migrations.RunPython.noop),
    ]
