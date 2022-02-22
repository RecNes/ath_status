from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from all_time_high.models import ExchangeCurrency, ExchangeRate
from all_time_high.views import get_exchange_rate


class Command(BaseCommand):
    help = _("Kur fiyatlarını çeker")

    def handle(self, *args, **options):
        exchange_currencies = ExchangeCurrency.objects.all()
        for exchange_currency in exchange_currencies:
            try:
                currency = get_exchange_rate(
                    from_currency=exchange_currency.base,
                    to_currency=exchange_currency.target,
                    currency_amount=1)

                last_rate = ExchangeRate.objects.filter(currency=currency).last()
                self.stdout.write(
                    self.style.SUCCESS(f"{last_rate}")
                )
            except Exception as uee:
                self.stdout.write(
                    self.style.ERROR(f"{exchange_currency}:\r\n{uee}")
                )
