from django.db.models.signals import post_save
from django.dispatch import receiver

from all_time_high.management.commands import notify
from all_time_high.models import AllTimeHigh, OneUnitDropped


@receiver(post_save, sender=AllTimeHigh, dispatch_uid="post_ath_message")
def post_ath_message(sender, instance, raw, *args, **kwargs):
    notification_settings = notify.get_notification_settings()
    notify.post_ath_message(notification_settings)


@receiver(post_save, sender=OneUnitDropped, dispatch_uid="post_oud_message")
def post_oud_message(sender, instance, raw, *args, **kwargs):
    notification_settings = notify.get_notification_settings()
    notify.post_oud_message(notification_settings)
