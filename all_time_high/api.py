import tweepy
from django.conf import settings


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
