from decimal import Decimal

from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
    DecimalValidator,
    MinValueValidator
)
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import ugettext_lazy as _


class ExchangeCurrency(models.Model):
    base = models.CharField(
        verbose_name=_("Para Birimi 1"),
        max_length=3,
        validators=[
            MaxLengthValidator(3),
            MinLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )
    target = models.CharField(
        verbose_name=_("Para Birimi 2"),
        max_length=3,
        validators=[
            MaxLengthValidator(3),
            MinLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )

    def __str__(self):
        return f"{self.base} X {self.target}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["base", "target"],
                name='unique_exchange_currencies'
            )
        ]
        indexes = [
            models.Index(fields=["base", "target"]),
        ]


class ExchangeRate(models.Model):
    currency = models.ForeignKey(
        to="ExchangeCurrency",
        verbose_name=_("Kur Birimleri"),
        on_delete=models.CASCADE
    )
    exchange_rate = models.DecimalField(
        verbose_name=_("Güncel Kur"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            DecimalValidator(10, 2),
            MinValueValidator(Decimal("0.0")),
        ]
    )
    record_date = models.DateTimeField(
        verbose_name=_("Kayıt Tarihi"),
        auto_now_add=True
    )

    def __str__(self):
        return _("Güncel Kur:") + f" {self.exchange_rate}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["exchange_rate", "record_date"],
                name='unique_exchange_rate'
            )
        ]
        indexes = [
            models.Index(fields=["currency"]),
            models.Index(fields=["record_date"]),
        ]


class AllTimeHigh(models.Model):
    currency = models.OneToOneField(
        to="ExchangeCurrency",
        verbose_name=_("Kur Birimleri"),
        on_delete=models.CASCADE
    )
    exchange_rate = models.DecimalField(
        verbose_name=_("Tüm Zamanların En Yüksek Kuru"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            DecimalValidator(10, 2),
            MinValueValidator(Decimal("0.0")),
        ]
    )
    update_date = models.DateTimeField(
        verbose_name=_("Güncelleme Tarihi"),
        auto_now=True
    )
    notify = models.BooleanField(
        verbose_name=_("Bildir"),
        default=False
    )

    def __str__(self):
        return _("Tüm Zamanların En Yüksek Kuru: ") + f"{self.currency} = {self.exchange_rate}"


class OneUnitDropped(models.Model):
    currency = models.OneToOneField(
        to="ExchangeCurrency",
        verbose_name=_("Kur Birimleri"),
        on_delete=models.CASCADE
    )
    exchange_rate = models.DecimalField(
        verbose_name=_("1 Birim Düşüş Kaydı"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            DecimalValidator(10, 2),
            MinValueValidator(Decimal("0.0")),
        ]
    )
    update_date = models.DateTimeField(
        verbose_name=_("Güncelleme Tarihi"),
        auto_now=True
    )
    notify = models.BooleanField(
        verbose_name=_("Bildir"),
        default=False
    )

    def __str__(self):
        return _("Son 1 Birim Düşüş Kuru: ") + f"{self.currency} = {self.exchange_rate}"
