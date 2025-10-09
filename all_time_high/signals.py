from django.db.models.signals import post_save
from django.dispatch import receiver

from all_time_high.management.commands import notify
from all_time_high.models import AllTimeHigh, DailyLowestPrice


@receiver(post_save, sender=AllTimeHigh, dispatch_uid="post_ath_message")
def post_ath_message(sender, instance, raw, *args, **kwargs):
    """
    Post ath message via triggered signal
    :param sender:
    :param instance:
    :param raw:
    :param args:
    :param kwargs:
    :return:
    """
    notification_settings = notify.get_notification_settings()
    notify.post_ath_message(notification_settings)


@receiver(post_save, sender=DailyLowestPrice, dispatch_uid="post_oud_message")
def post_oud_message(sender, instance, raw, *args, **kwargs):
    """
    Post daily lowest price message via signal
    :param sender:
    :param instance:
    :param raw:
    :param args:
    :param kwargs:
    :return:
    """
    notification_settings = notify.get_notification_settings()
    notify.post_oud_message(notification_settings)
