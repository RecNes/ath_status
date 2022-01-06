import json

import requests
import tweepy
from django.conf import settings
from django.utils import timezone
from google_currency import convert
from telegram_notifier import TelegramNotifier


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
