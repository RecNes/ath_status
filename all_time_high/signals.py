from django.db.models.signals import post_save
from django.dispatch import receiver

from all_time_high.api import to_twitter
from all_time_high.models import AllTimeHighRate


def create_message(instance):
    return f'''Yeni ATH oluştu:<br/> 
    "{instance.currency_1}" x "{instance.currency_2}" : {instance.exchange_rate}
    '''


@receiver(post_save, sender=AllTimeHighRate, dispatch_uid="send_ath_to_twitter")
def send_ath_to_twitter(sender, instance, raw, *args, **kwargs):
    to_twitter(create_message(instance))
