from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from all_time_high.api import to_telegram, to_twitter
from all_time_high.models import AllTimeHigh, NotificationSetting, OneUnitDropped


def create_ath_message(instance):
    return f'''⁃ Yeni ATH:
 
$ 1.00 = {instance.exchange_rate} ₺ 

◦ ATH: Tüm zamanların en yükseği
◦ Otomatik mesaj http://atshstatus.recnes.com/'''


def create_oud_message(instance):
    """
    Create notification message
    :param instance:
    :return:
    """
    return f'''⁃ 1 Birimlik Düşüş Yaşandı:
 
$ 1.00 = {instance.exchange_rate} ₺ 

◦ Bu mesaj otomatik olarak oluşturulmuştur.
◦ Otomatik mesaj http://atshstatus.recnes.com/'''


def is_certain_minutes_passed_from_last_notification(instance, minutes=5):
    """
    Certain time has to be passed before the last notification was sent
    :param instance:
    :param minutes:
    :return:
    """
    if instance.last_notification_date + timedelta(minutes=minutes) < timezone.now():
        return True
    return False


def get_notification_settings():
    """
    Return notification settings
    :return:
    """
    return NotificationSetting.objects.last()


def is_it_time(instance, interval):
    """
    Is it time to sent new notification?
    :param instance:
    :param interval:
    :return:
    """
    return instance.last_notification_date + timedelta(minutes=interval) < timezone.now()


def send_notifications(instance, notification_settings, message):
    """
    Notify the channels
    :param instance:
    :param notification_settings:
    :param message:
    :return:
    """
    if not instance.notify:
        return

    notify = notification_settings.is_telegram_enabled
    its_time = is_it_time(instance, notification_settings.telegram_notification_interval)
    if notify and its_time:
        to_telegram(message)

    notify = notification_settings.is_twitter_enabled
    its_time = is_it_time(instance, notification_settings.twitter_notification_interval)
    if notify and its_time:
        to_twitter(message)

    instance.notify = False
    instance.last_notification_date = timezone.now()
    instance.save(update_fields=["notify", "last_notification_date"])


def post_ath_message(notification_settings):
    """
    Post the ath message
    :param notification_settings:
    :return:
    """
    instance = AllTimeHigh.objects.last()
    message = create_ath_message(instance)
    send_notifications(instance, notification_settings, message)


def post_oud_message(notification_settings):
    """
    Post the one unit dropped message
    :param notification_settings:
    :return:
    """
    instance = OneUnitDropped.objects.all()
    message = create_oud_message(instance)
    send_notifications(instance, notification_settings, message)


class Command(BaseCommand):
    help = _("ilgili yerlere bildirimleri gönderir")

    def handle(self, *args, **options):
        notification_settings = get_notification_settings()
        post_ath_message(notification_settings)
        post_oud_message(notification_settings)
