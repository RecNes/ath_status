from decimal import Decimal

from django.shortcuts import render

from all_time_high.api import from_google_exchange_rates, from_open_exchange_rates, from_abstractapi_exchange_rates
from all_time_high.models import ExchangeCurrency, AllTimeHigh, OneUnitDropped, ExchangeRate


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
        "oxr_rate": from_open_exchange_rates(**kwargs),
        "abstractapi_rate": from_abstractapi_exchange_rates(**kwargs),
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
    currency.exchangerate_set.add(exchange_rate_obj, bulk=False)

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
    one_unit_dropped = one_unit_drop.exchange_rate.quantize(Decimal("0")) - rounded_lowest_rate >= 1
    if no_one_unit_drop or one_unit_dropped:
        one_unit_drop, created = OneUnitDropped.objects.get_or_create(
            currency=currency
        )
        one_unit_drop.exchange_rate = rounded_lowest_rate
        one_unit_drop.notify = True
        one_unit_drop.save()

    return currency


def one_page_view(request):
    template = "one_page_template.html"
    content = {
        "exchange_currencies": ExchangeCurrency.objects.all()
    }
    return render(request, template, context=content)
