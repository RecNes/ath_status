from django.db.models.signals import post_save
from django.dispatch import receiver

from all_time_high.api import to_twitter, to_telegram
from all_time_high.models import AllTimeHighRate


def create_message(instance):
    return f'''⁃ Yeni ATH:
 
$ 1.00 = {instance.exchange_rate} ₺ 

◦ ATH: Tüm zamanların en yükseği
◦ Bu mesaj otomatik olarak oluşturulmuştur.'''


@receiver(post_save, sender=AllTimeHighRate, dispatch_uid="send_ath_to_twitter")
def send_ath_to_twitter(sender, instance, raw, *args, **kwargs):
    message = create_message(instance)
    to_telegram(message)
    to_twitter(message)
