from rest_framework.views import APIView
from datetime import timedelta
from decimal import Decimal

from django.db.models import Max
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from all_time_high.api import (
    from_exchangerateapi_exchange_rates,
    from_frankfurter_exchange_rates,
)
from all_time_high.models import (
    ExchangeCurrency,
    AllTimeHigh,
    DailyLowestPrice,
    ExchangeRate,
)
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


def get_exchange_rate(
    from_currency="usd", to_currency="try", currency_amount=1
) -> object:
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
        "currency_amount": currency_amount,
    }

    latest_rates = {
        # "google_rate": from_google_exchange_rates(**kwargs),
        # "oxr_rate": from_open_exchange_rates(**kwargs),
        # "abstractapi_rate": from_abstractapi_exchange_rates(**kwargs),
        "exchangerateapi_rate": from_exchangerateapi_exchange_rates(**kwargs),
        "frankfurter_rate": from_frankfurter_exchange_rates(**kwargs),
    }

    highest_rate = get_higher_rate(latest_rates)
    lowest_rate = get_lowest_rate(latest_rates)
    if all((lowest_rate < 1, highest_rate < 1)):
        raise ValueError(
            _(
                f"Oranlar geçerli değil. En düşük: {str(lowest_rate)} / En yüksek: {str(highest_rate)}"
            )
        )
    if lowest_rate < 1 <= highest_rate:
        lowest_rate = highest_rate
    if lowest_rate < 1:
        raise ValueError(
            _(
                f"Oranlar geçerli değil. En düşük: {str(lowest_rate)} / En yüksek: {str(highest_rate)}"
            )
        )

    currency, _ = ExchangeCurrency.objects.get_or_create(
        base=from_currency.lower(),
        target=to_currency.lower(),
    )
    current_exchange_rate = highest_rate.quantize(Decimal("0.00"))
    exchange_rate_obj = ExchangeRate(exchange_rate=current_exchange_rate)
    currency.rates.add(exchange_rate_obj, bulk=False)  # type: ignore

    try:
        all_time_high = currency.alltimehigh  # type: ignore
    except AllTimeHigh.DoesNotExist:
        all_time_high = None

    if all_time_high is None or current_exchange_rate > all_time_high.exchange_rate:
        all_time_high, created = AllTimeHigh.objects.get_or_create(currency=currency)
        all_time_high.exchange_rate = current_exchange_rate
        all_time_high.notify = True
        all_time_high.save()

    try:
        daily_lowest = currency.dailylowestprice  # type: ignore
    except DailyLowestPrice.DoesNotExist:
        daily_lowest = None

    no_daily_lowest = daily_lowest is None or daily_lowest.daily_lowest_price <= 0
    rounded_lowest_rate = lowest_rate.quantize(Decimal("0"))
    # Eğer yeni gelen fiyat daha düşükse veya hiç kayıt yoksa güncelle
    if no_daily_lowest or rounded_lowest_rate < daily_lowest.daily_lowest_price:  # type: ignore
        daily_lowest, created = DailyLowestPrice.objects.get_or_create(
            currency=currency
        )
        daily_lowest.daily_lowest_price = rounded_lowest_rate
        daily_lowest.notify = True
        daily_lowest.save()

    return currency


@ensure_csrf_cookie
def one_page_view(request):
    template = "one_page_template.html"
    content = {
        "exchange_currencies": ExchangeCurrency.objects.all(),
        "graph_day_range": settings.GRAPH_DATE_RANGE,
    }
    return render(request, template, context=content)


class ExchangeGraphView(ListAPIView):
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        """
        This view returns the highest rate per day for the selected exchange in the last 30 days.
        """
        from django.db.models import Max

        date_range_end = timezone.now()
        date_range_start = date_range_end - timedelta(days=30)
        exchange_currency = ExchangeCurrency.objects.get(pk=self.kwargs["pk"])
        rates = (
            exchange_currency.rates.filter(  # type: ignore
                record_date__gte=date_range_start,
                record_date__lt=date_range_end,
            )
            .extra({"day": "date(record_date)"})
            .values("day")
            .annotate(max_rate=Max("exchange_rate"))
            .order_by("day")
        )
        return rates

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = [
            {"record_date": r["day"], "exchange_rate": r["max_rate"]} for r in queryset
        ]
        return Response(response_data)


class BulkExchangeGraphView(APIView):
    def get(self, request):
        date_range_end = (timezone.now()).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        date_range_start = (date_range_end - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = {}

        for currency in ExchangeCurrency.objects.all():
            rates = (
                currency.rates.filter(  # type: ignore
                    record_date__gte=date_range_start,
                    record_date__lt=date_range_end,
                )
                .extra({"day": "date(record_date)"})
                .values("day")
                .annotate(max_rate=Max("exchange_rate"))
                .order_by("day")
            )
            serializer_data = [
                {"record_date": r["day"], "exchange_rate": r["max_rate"]} for r in rates
            ]
            result[str(currency.id)] = serializer_data  # type: ignore
        return Response(result)
