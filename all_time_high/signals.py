import time

from django.db.models.signals import post_save
from django.dispatch import receiver

from all_time_high.api import to_twitter, to_telegram
from all_time_high.models import ExchangeRate, AllTimeHigh, OneUnitDropped


def create_message(instance):
    return f'''⁃ Yeni ATH:
 
$ 1.00 = {instance.all_time_high_rate} ₺ 

◦ ATH: Tüm zamanların en yükseği
◦ Bu mesaj otomatik olarak oluşturulmuştur.'''


def is_half_hour():
    minute = time.localtime().tm_min
    if minute in [0, 30]:
        return True
    return False


# @receiver(post_save, sender=AllTimeHigh, dispatch_uid="post_ath_message")
def post_ath_message(sender, instance, raw, *args, **kwargs):

    if not is_half_hour():
        return

    if not instance.notify:
        return

    message = create_message(instance)
    to_telegram(message)
    # to_twitter(message)

    instance.notify = False
