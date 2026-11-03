from datetime import datetime, timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PredictDemandRequestSerializer
from .services.forecast import run_forecast
from .services.series import build_daily_series

SERVICE_NAME = "marketreach-ai-service"
DEMO_DISCLAIMER = (
    "DEMONSTRATION ONLY: this forecast was produced from synthetic demo data, "
    "not real sales records."
)


def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class HealthView(APIView):
    """GET /api/v1/health - public, no secrets exposed."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "MarketReach AI forecasting service is healthy",
                "data": {"service": SERVICE_NAME, "timestamp": _utc_now()},
            }
        )


class PredictDemandView(APIView):
    """POST /api/v1/predict-demand - requires the X-API-Key header."""

    def post(self, request):
        serializer = PredictDemandRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        series = build_daily_series(payload["historicalSales"])
        result = run_forecast(series, payload["forecastDays"], payload["method"])

        is_demo = payload["dataSource"] == "synthetic_demo"
        data = {
            "productId": payload["productId"],
            "retailerId": payload["retailerId"],
            "forecastDays": payload["forecastDays"],
            "predictedDemand": result.predicted_demand,
            "model": result.model,
            "dataSource": payload["dataSource"],
            "generatedAt": _utc_now(),
            # Additional, explainable fields (safe for clients to ignore):
            "averageDailyDemand": result.average_daily_demand,
            "historyDays": result.history_days,
            "dailyForecast": result.daily,
            "explanation": result.explanation,
            "isDemonstration": is_demo,
            "warnings": result.warnings,
        }
        if result.selection_note:
            data["selectionNote"] = result.selection_note
        if is_demo:
            data["disclaimer"] = DEMO_DISCLAIMER

        return Response(
            {"success": True, "message": "Demand forecast generated successfully", "data": data}
        )
