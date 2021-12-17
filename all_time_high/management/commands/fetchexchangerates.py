import json
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from google_currency import convert

from all_time_high.models import AllTimeHighRate


class Command(BaseCommand):
    help = _("Kur fiyatlarını çeker")

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        response = json.loads(convert("usd", "try", 1))
        currency, created = AllTimeHighRate.objects.get_or_create(
            currency_1=response["from"].lower(),
            currency_2=response["to"].lower(),
        )

        currency.exchange_rate = Decimal(response["amount"]).quantize(Decimal("0.00"))
        if currency.all_time_high_rate is None or currency.exchange_rate > currency.all_time_high_rate:
            currency.all_time_high_rate = currency.exchange_rate
            currency.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'"{currency.currency_1}" x "{currency.currency_2}" : {currency.exchange_rate}'
            )
        )
