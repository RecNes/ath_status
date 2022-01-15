# Register your models here.
from django.contrib import admin

from all_time_high.models import NotificationSetting, ExchangeCurrency, ExchangeRate, AllTimeHigh, OneUnitDropped

admin.site.register(ExchangeCurrency)
admin.site.register(ExchangeRate)
admin.site.register(AllTimeHigh)
admin.site.register(OneUnitDropped)
admin.site.register(NotificationSetting)
