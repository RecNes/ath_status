import os
import datetime
import json
import requests
import tweepy
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from google_currency import convert
from telegram_notifier import TelegramNotifier


EXCHANGERATEAPI_COUNTER_FILE = os.path.join(os.path.dirname(__file__), "exchangerateapi_counter.txt")
EXCHANGERATEAPI_LAST_REQUEST_FILE = os.path.join(os.path.dirname(__file__), "exchangerateapi_last_request.txt")


def to_twitter(message):
    """
    Send message to Twitter
    :param message:
    :return:
    """
    auth = tweepy.OAuthHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SEC
    )
    auth.set_access_token(
        settings.TWITTER_TOKEN,
        settings.TWITTER_TOKEN_SEC
    )
    api = tweepy.API(auth)

    try:
        api.update_status(message)
    except tweepy.HTTPException as error:
        for api_code in error.api_codes:
            if api_code == 187:
                print('duplicate message')


def get_telegram_chat_ids():
    """
    Get telegram chat ids that the bot is in.
    :return:
    """
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT}/getUpdates"
    response = requests.get(url)
    content = response.json()
    result = list()
    if not response.status_code >= 300:
        if content["ok"]:
            result = content["result"]

    chat_ids = list()
    for item in result:
        if "message" not in item.keys():
            continue

        message = item["message"]
        if "chat" not in message.keys():
            continue

        chat = message["chat"]
        if "id" not in chat:
            continue

        chat_id = chat["id"]
        if chat_id not in chat_ids:
            chat_ids.append(chat_id)

    return chat_ids


def to_telegram(message):
    """
    Send message to telegram via bot
    :param message:
    :return:
    """
    chat_ids = get_telegram_chat_ids()
    for chat_id in chat_ids:
        notifier = TelegramNotifier(settings.TELEGRAM_BOT, chat_id=chat_id, parse_mode="HTML")
        notifier.send(message)


def from_google_exchange_rates(from_currency="usd", to_currency="try", currency_amount=1):
    """
    Fetches exchange rate from Google in any time

    :param from_currency:
    :param to_currency:
    :param currency_amount:
    :return:
    """
    rate = json.loads(convert(from_currency, to_currency, currency_amount))
    return rate["amount"]


def from_open_exchange_rates(from_currency="usd", to_currency="try", currency_amount=1):
    """
    Fetches exchange rate from Open Exchange Rates in daily basis
    https://docs.openexchangerates.org/docs/

    :param from_currency:
    :param to_currency:
    :param currency_amount:
    :return:
    """
    rate = None
    now = timezone.now()
    if now.hour == 12 and now.minute == 0:
        payload = {"app_id": settings.OPEN_EXCHANGE_RATES}
        request_url = "http://openexchangerates.org/api/latest.json"
        json_response = requests.get(request_url, params=payload)
        response_content = json_response.json()
        rate = response_content['rates'][to_currency.upper()]
    return rate


def from_abstractapi_exchange_rates(from_currency="usd", to_currency="try", currency_amount=1):
    """
    Fetches exchange rate from AbstractAPI Exchange Rates in 2 days basis
    https://app.abstractapi.com/api/exchange-rates/documentation

    :param from_currency:
    :param to_currency:
    :param currency_amount:
    :return:
    """
    rate = None
    now = timezone.now()
    if now.day % 2 == 0 and now.hour == 12 and now.minute == 0:
        url = "https://exchange-rates.abstractapi.com/v1/live/"
        payload = {
            "api_key": settings.ABSTRACTAPI_API_KEY,
            "base": from_currency.upper(),
            "target": to_currency.upper()
        }
        json_response = requests.get(url, params=payload)
        content = json_response.json()
        rate = content["exchange_rates"][to_currency.upper()]
    return rate


def _get_exchangerateapi_counter():
    today = datetime.date.today()
    try:
        with open(EXCHANGERATEAPI_COUNTER_FILE, "r") as f:
            line = f.read().strip()
            if line:
                date_str, count_str = line.split(",")
                last_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                count = int(count_str)
                # Reset counter if today is 29th or month changed
                if today.day == 29 or today.month != last_date.month:
                    return today, 0
                return last_date, count
    except Exception:
        pass
    return today, 0


def _get_exchangerateapi_last_request():
    try:
        with open(EXCHANGERATEAPI_LAST_REQUEST_FILE, "r") as f:
            line = f.read().strip()
            if line:
                return datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return None


def _set_exchangerateapi_last_request(dt):
    with open(EXCHANGERATEAPI_LAST_REQUEST_FILE, "w") as f:
        f.write(dt.strftime("%Y-%m-%d %H:%M:%S"))


def _set_exchangerateapi_counter(date, count):
    with open(EXCHANGERATEAPI_COUNTER_FILE, "w") as f:
        f.write(f"{date.isoformat()},{count}")


def from_exchangerateapi_exchange_rates(from_currency="usd", to_currency="try", currency_amount=1):
    """
    Fetches exchange rate from exchangerate-api.com with monthly, daily and hourly limit
    Docs: https://www.exchangerate-api.com/docs/overview
    """
    rate = None
    now = datetime.datetime.now()
    today = now.date()
    last_date, count = _get_exchangerateapi_counter()

    days_in_month = (datetime.date(today.year, today.month % 12 + 1, 1) - datetime.timedelta(days=1)).day
    daily_limit = int(1500 / days_in_month)
    hourly_interval = int(24 / daily_limit) if daily_limit else 24

    last_request = _get_exchangerateapi_last_request()
    if last_request:
        delta = now - last_request
        if delta.total_seconds() < hourly_interval * 3600:
            return None

    if today.day == 29 or today.month != last_date.month:
        count = 0
    if count >= 1500:
        return None
    try:
        url = (
            f"https://v6.exchangerate-api.com/v6/"
            f"{settings.EXCHANGERATEAPI_API_KEY}/pair/"
            f"{from_currency.upper()}/{to_currency.upper()}"
        )
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and "conversion_rate" in data:
            rate = (
                Decimal(str(data["conversion_rate"])) *
                Decimal(str(currency_amount))
            )
            _set_exchangerateapi_counter(today, count + 1)
            _set_exchangerateapi_last_request(now)
    except Exception:
        pass
    return rate


def from_frankfurter_exchange_rates(from_currency="usd", to_currency="try", currency_amount=1):
    """
    Fetches exchange rate from frankfurter.dev
    Docs: https://www.frankfurter.app/docs

    :param from_currency:
    :param to_currency:
    :param currency_amount:
    :return:
    """
    rate = None
    try:
        url = (
            f"https://api.frankfurter.app/latest?amount={currency_amount}"
            f"&from={from_currency.upper()}&to={to_currency.upper()}"
        )
        response = requests.get(url)
        data = response.json()
        if (
            response.status_code == 200 and
            "rates" in data and
            to_currency.upper() in data["rates"]
        ):
            rate = Decimal(str(data["rates"][to_currency.upper()]))
    except Exception:
        pass
    return rate
