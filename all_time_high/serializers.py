from rest_framework import serializers

from all_time_high.models import ExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = (
            "daily_lowest_price",
            "record_date",
        )
