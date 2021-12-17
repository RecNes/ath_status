import tweepy
from django.conf import settings
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
    except tweepy.TweepError as error:
        if error.api_code == 187:
            print('duplicate message')


def to_telegram(message):
    """
    Send message to telegram via bot
    :param message:
    :return:
    """
    token = settings.TELEGRAM_BOT
    chat_id = settings.TELEGRAM_CHAT_ID

    notifier = TelegramNotifier(token, chat_id=chat_id, parse_mode="HTML")
    notifier.send(message)
