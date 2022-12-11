from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from all_time_high.api import from_google_exchange_rates, from_open_exchange_rates, from_abstractapi_exchange_rates
from all_time_high.models import ExchangeCurrency, AllTimeHigh, OneUnitDropped, ExchangeRate
from all_time_high.serializers import ExchangeRateSerializer
from ath import settings


def get_higher_rate(latest_rates) -> Decimal:
    """
    Return highest rate
    :param latest_rates:
    :return:
    """
    values = [i for i in latest_rates.values() if i is not None]
    rate = 0
    if len(values):
        values.sort(reverse=True)
        rate = values[0]
    return Decimal(rate)


def get_lowest_rate(latest_rates) -> Decimal:
    """
    Return lowest rate
    :param latest_rates:
    :return:
    """
    values = [i for i in latest_rates.values() if i is not None]
    rate = 0
    if len(values):
        values.sort()
        rate = values[0]
    return Decimal(rate)


def get_exchange_rate(from_currency="usd", to_currency="try", currency_amount=1) -> object:
    """
    Fetch exchange rate and save to DB and return object.
    :param from_currency:
    :param to_currency:
    :param currency_amount:
    :return:
    """
    kwargs = {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "currency_amount": currency_amount
    }

    latest_rates = {
        "google_rate": from_google_exchange_rates(**kwargs),
        # "oxr_rate": from_open_exchange_rates(**kwargs),
        # "abstractapi_rate": from_abstractapi_exchange_rates(**kwargs),
    }

    highest_rate = get_higher_rate(latest_rates)
    lowest_rate = get_lowest_rate(latest_rates)
    if lowest_rate == 0:
        lowest_rate = highest_rate

    currency, created = ExchangeCurrency.objects.get_or_create(
        base=from_currency.lower(),
        target=to_currency.lower(),
    )
    current_exchange_rate = highest_rate.quantize(Decimal("0.00"))
    exchange_rate_obj = ExchangeRate(
        exchange_rate=current_exchange_rate
    )
    currency.rates.add(exchange_rate_obj, bulk=False)

    try:
        all_time_high = currency.alltimehigh
    except AllTimeHigh.DoesNotExist:
        all_time_high = None

    if all_time_high is None or current_exchange_rate > all_time_high.exchange_rate:
        all_time_high, created = AllTimeHigh.objects.get_or_create(
            currency=currency
        )
        all_time_high.exchange_rate = current_exchange_rate
        all_time_high.notify = True
        all_time_high.save()

    try:
        one_unit_drop = currency.oneunitdropped
    except OneUnitDropped.DoesNotExist:
        one_unit_drop = None

    no_one_unit_drop = one_unit_drop is None or one_unit_drop.exchange_rate <= 0
    rounded_lowest_rate = lowest_rate.quantize(Decimal("0"))
    one_unit_dropped = None
    if one_unit_drop:
        one_unit_dropped = one_unit_drop.exchange_rate.quantize(Decimal("0")) - rounded_lowest_rate >= 1
    if no_one_unit_drop or one_unit_dropped:
        one_unit_drop, created = OneUnitDropped.objects.get_or_create(
            currency=currency
        )
        one_unit_drop.exchange_rate = rounded_lowest_rate
        one_unit_drop.notify = True
        one_unit_drop.save()

    return currency


@ensure_csrf_cookie
def one_page_view(request):
    template = "one_page_template.html"
    content = {
        "exchange_currencies": ExchangeCurrency.objects.all(),
        "graph_day_range": settings.GRAPH_DATE_RANGE
    }
    return render(request, template, context=content)


class ExchangeGraphView(ListAPIView):
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        """
        This view is return a list of all the rates of selected exchange in date range.
        """
        date_range_end = timezone.now()
        date_range_start = date_range_end - timedelta(hours=settings.GRAPH_DATE_RANGE)
        exchange_currency = ExchangeCurrency.objects.get(pk=self.kwargs["pk"])
        exchange_rates = exchange_currency.rates.filter(
            record_date__gte=date_range_start,
            record_date__lt=date_range_end,
        )
        return exchange_rates

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
