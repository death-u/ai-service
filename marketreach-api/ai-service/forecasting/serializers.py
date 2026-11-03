"""Request validation for POST /api/v1/predict-demand."""
import math

from django.conf import settings
from rest_framework import serializers

METHOD_CHOICES = ["moving_average", "seasonal_average", "auto"]
DATA_SOURCE_CHOICES = ["historical_sales", "synthetic_demo"]


class SalesPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    quantity = serializers.FloatField(min_value=0)

    def validate_quantity(self, value):
        if not math.isfinite(value):
            raise serializers.ValidationError("Quantity must be a finite number.")
        return value


class PredictDemandRequestSerializer(serializers.Serializer):
    productId = serializers.CharField(max_length=100)
    retailerId = serializers.CharField(max_length=100)
    forecastDays = serializers.IntegerField(min_value=1)
    historicalSales = SalesPointSerializer(many=True, allow_empty=False)

    # Optional extras (the base contract works without them).
    method = serializers.ChoiceField(choices=METHOD_CHOICES, required=False, default="moving_average")
    dataSource = serializers.ChoiceField(
        choices=DATA_SOURCE_CHOICES, required=False, default="historical_sales"
    )

    def validate_forecastDays(self, value):
        if value > settings.FORECAST_MAX_DAYS:
            raise serializers.ValidationError(
                f"forecastDays must be between 1 and {settings.FORECAST_MAX_DAYS}."
            )
        return value

    def validate_historicalSales(self, value):
        if len(value) > settings.MAX_HISTORY_ROWS:
            raise serializers.ValidationError(
                f"historicalSales may contain at most {settings.MAX_HISTORY_ROWS} records."
            )
        return value
