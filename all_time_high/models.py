from decimal import Decimal

from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
    DecimalValidator,
    MinValueValidator,
    EmailValidator
)
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import ugettext_lazy as _


class ExchangeCurrency(models.Model):
    """
    Exchange currency model
    """
    base = models.CharField(
        verbose_name=_("Para Birimi 1"),
        max_length=3,
        validators=[
            MaxLengthValidator(3),
            MinLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )
    base_symbol = models.CharField(
        verbose_name=_("Para Birimi 1 Sembolü"),
        max_length=3,
        null=True,
        blank=True,
        validators=[
            MaxLengthValidator(3),
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
    target_symbol = models.CharField(
        verbose_name=_("Para Birimi 2 Sembolü"),
        max_length=3,
        null=True,
        blank=True,
        validators=[
            MaxLengthValidator(3),
            ProhibitNullCharactersValidator()
        ]
    )

    def __str__(self):
        base_currency_text = f"{self.base.upper()}"
        if self.base_symbol is not None:
            base_currency_text += f" ({self.base_symbol})"
        target_currency_text = f"{self.target.upper()}"
        if self.target_symbol is not None:
            target_currency_text += f" ({self.target_symbol})"
        return f"{base_currency_text} <> {target_currency_text}"

    class Meta:
        verbose_name = _("Para Birimi")
        verbose_name_plural = _("Para Birimleri")
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
    """
    Exchange rate model
    """
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
        verbose_name = _("Kur Oranı")
        verbose_name_plural = _("Kur Oranları")
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
    """
    All time high model
    """
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
    last_notification_date = models.DateTimeField(
        verbose_name=_("Son Bildirim Zamanı"),
        null=True,
        blank=False,
        editable=False
    )

    def __str__(self):
        return _("Tüm Zamanların En Yüksek Kuru: ") + f"{self.currency} = {self.exchange_rate}"

    class Meta:
        verbose_name = _("Tüm Zamanların En Yüksek Kuru")
        verbose_name_plural = _("Tüm Zamanların En Yüksek Kuru")


class OneUnitDropped(models.Model):
    """
    One unit dropped model
    """
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
    last_notification_date = models.DateTimeField(
        verbose_name=_("Son Bildirim Zamanı"),
        null=True,
        blank=False,
        editable=False
    )

    def __str__(self):
        return _("Son 1 Birim Düşüş Rakamı: ") + f"{self.currency} = {self.exchange_rate}"

    class Meta:
        verbose_name = _("1 Birim Düşüş")
        verbose_name_plural = _("1 Birim Düşüş")


class NotificationSetting(models.Model):
    """
    Notification settings model
    """
    is_telegram_enabled = models.BooleanField(
        verbose_name=_("Telegram Bildirimi Açık"),
        default=True
    )
    telegram_notification_interval = models.PositiveSmallIntegerField(
        verbose_name=_("Telegram'a Mesaj Gönderme Sıklığı"),
        help_text=_("Dakika bazında"),
        default=30
    )
    is_twitter_enabled = models.BooleanField(
        verbose_name=_("Twitter Bildirimi Açık"),
        default=True
    )
    twitter_notification_interval = models.PositiveSmallIntegerField(
        verbose_name=_("Twitter'a Mesaj Gönderme Sıklığı"),
        help_text=_("Dakika bazında"),
        default=30
    )
    is_email_list_enabled = models.BooleanField(
        verbose_name=_("Eposta Listesi Bildirimi Açık"),
        default=True
    )
    email_list_notification_interval = models.PositiveSmallIntegerField(
        verbose_name=_("Eposta Listesi'ne Mesaj Gönderme Sıklığı"),
        help_text=_("Dakika bazında"),
        default=30
    )

    def __str__(self):
        return str(_("Bildirim ayarları"))

    class Meta:
        verbose_name = _("Bildirim Ayarı")
        verbose_name_plural = _("Bildirim Ayarları")


class NotificationEmails(models.Model):
    email = models.EmailField(
        verbose_name=_("Eposta Adresi"),
        max_length=255,
        validators=[
            EmailValidator(message=_("Geçerli bir eposta adresi girin.")),
            MaxLengthValidator(255),
            MinLengthValidator(5),
            ProhibitNullCharactersValidator()
        ]
    )
    register_date = models.DateTimeField(
        verbose_name=_("Kayıt Tarihi"),
        auto_now_add=True
    )
    last_notified_at = models.DateTimeField(
        verbose_name=_("Son Bildirim Gönderme Tarihi"),
        auto_now=True
    )

    def __str__(self):
        return str(_("Bildirim ayarları"))

    class Meta:
        verbose_name = _("Eposta Adresi")
        verbose_name_plural = _("Eposta Adresleri")
