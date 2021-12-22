from decimal import Decimal

from django.core.validators import (
    MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator,
    DecimalValidator, MinValueValidator
)
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AllTimeHighRate(models.Model):
    currency_1 = models.CharField(
        verbose_name=_("Para Birimi 1"),
        max_length=3,
        validators=[
            MaxLengthValidator(3),
            MinLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )

    currency_2 = models.CharField(
        verbose_name=_("Para Birimi 2"),
        max_length=3,
        validators=[
            MaxLengthValidator(3),
            MinLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )

    exchange_rate = models.DecimalField(
        verbose_name=_("Güncel Kur"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=False,
        validators=[
            DecimalValidator(10, 2),
            MinValueValidator(Decimal("0.0")),
        ]
    )

    all_time_high_rate = models.DecimalField(
        verbose_name=_("Tüm Zamanların En Yüksek Kuru"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=False,
        validators=[
            DecimalValidator(10, 2),
            MinValueValidator(Decimal("0.0")),
        ]
    )

    notify = models.BooleanField(
        verbose_name=_("Bildir"),
        default=False
    )
