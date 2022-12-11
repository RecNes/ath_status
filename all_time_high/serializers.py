from rest_framework import serializers

from all_time_high.models import ExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = (
            "exchange_rate",
            "record_date",
        )
