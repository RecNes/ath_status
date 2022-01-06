from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from all_time_high.views import get_exchange_rate


class Command(BaseCommand):
    help = _("Kur fiyatlarını çeker")

    def handle(self, *args, **options):
        currency = get_exchange_rate(from_currency="usd", to_currency="try", currency_amount=1)

        self.stdout.write(
            self.style.SUCCESS(
                f'"{currency.base.upper()}" x "{currency.target.upper()}" {currency.exchangerate_set.last()}'
            )
        )
