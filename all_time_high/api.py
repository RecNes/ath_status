from time import sleep

from telegram_notifier import TelegramNotifier
from django.conf import settings
import telegram_send
import telegram


class Send:

    def to_twitter(self, message):
        """
        Send message to Twitter
        :param message:
        :return:
        """



def run(message):
    """Start the bot."""
    token = settings.env_vars["TELEGRAM_BOT"]
    notifier = TelegramNotifier(token, chat_id="150514167", parse_mode="HTML")
    notifier.send(message)
    chat_id = "@+VOAW_19yHaRU_xzd"
    try:
        bot = telegram.Bot(token)
        bot_name = bot.get_me().username
    except:
        print("Something went wrong, please try again.")

    authorized = False
    while not authorized:
        try:
            bot.send_chat_action(chat_id=chat_id, action="typing")
            authorized = True
        except (telegram.error.Unauthorized, telegram.error.BadRequest):
            # Telegram returns a BadRequest when a non-admin bot tries to send to a private channel
            print(
                "Please add {} as administrator to your channel and press Enter".format(
                    bot_name
                )
            )
            sleep(3)

    request = telegram.utils.request.Request(read_timeout=timeout)
    bot = telegram.Bot(token, request=request)

