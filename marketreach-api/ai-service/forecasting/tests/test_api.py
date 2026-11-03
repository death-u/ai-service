import copy

from django.test import override_settings
from rest_framework.test import APISimpleTestCase

KEY = "test-key-123"
URL = "/api/v1/predict-demand"

# The exact example from the team's allocation document.
DOC_PAYLOAD = {
    "productId": "product_001",
    "retailerId": "retailer_001",
    "forecastDays": 7,
    "historicalSales": [
        {"date": "2026-10-25", "quantity": 15},
        {"date": "2026-10-26", "quantity": 18},
    ],
}


def long_history(days=28):
    from datetime import date, timedelta

    start = date(2026, 10, 1)
    return [{"date": (start + timedelta(days=i)).isoformat(), "quantity": 10 + (i % 7)} for i in range(days)]


@override_settings(SERVICE_API_KEY=KEY)
class HealthTests(APISimpleTestCase):
    def test_health_is_public_and_standard_shape(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["service"], "marketreach-ai-service")
        self.assertIn("timestamp", body["data"])

    def test_health_accepts_trailing_slash(self):
        self.assertEqual(self.client.get("/api/v1/health/").status_code, 200)


@override_settings(SERVICE_API_KEY=KEY)
class AuthTests(APISimpleTestCase):
    def test_missing_key_is_401(self):
        response = self.client.post(URL, DOC_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])

    def test_wrong_key_is_401(self):
        response = self.client.post(URL, DOC_PAYLOAD, format="json", HTTP_X_API_KEY="nope")
        self.assertEqual(response.status_code, 401)

    @override_settings(SERVICE_API_KEY="")
    def test_service_fails_closed_when_key_not_configured(self):
        response = self.client.post(URL, DOC_PAYLOAD, format="json", HTTP_X_API_KEY="")
        self.assertEqual(response.status_code, 401)


@override_settings(SERVICE_API_KEY=KEY)
class PredictDemandTests(APISimpleTestCase):
    def post(self, payload):
        return self.client.post(URL, payload, format="json", HTTP_X_API_KEY=KEY)

    def test_document_example_matches_expected_forecast(self):
        response = self.post(DOC_PAYLOAD)
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["predictedDemand"], 116)  # mean 16.5 x 7 = 115.5 -> 116
        self.assertEqual(data["model"], "moving_average_v1")
        self.assertEqual(data["dataSource"], "historical_sales")
        self.assertEqual(data["productId"], "product_001")
        self.assertEqual(data["retailerId"], "retailer_001")
        self.assertEqual(data["forecastDays"], 7)
        self.assertTrue(data["generatedAt"].endswith("Z"))
        self.assertEqual(len(data["dailyForecast"]), 7)
        self.assertEqual(data["dailyForecast"][0]["date"], "2026-10-27")
        self.assertFalse(data["isDemonstration"])
        self.assertTrue(data["warnings"])  # short history warning

    def test_synthetic_data_is_labelled_as_demonstration(self):
        payload = copy.deepcopy(DOC_PAYLOAD)
        payload["dataSource"] = "synthetic_demo"
        data = self.post(payload).json()["data"]
        self.assertTrue(data["isDemonstration"])
        self.assertIn("DEMONSTRATION", data["disclaimer"])

    def test_duplicate_dates_are_summed(self):
        payload = copy.deepcopy(DOC_PAYLOAD)
        payload["historicalSales"] = [
            {"date": "2026-10-25", "quantity": 10},
            {"date": "2026-10-25", "quantity": 5},
            {"date": "2026-10-26", "quantity": 18},
        ]
        self.assertEqual(self.post(payload).json()["data"]["predictedDemand"], 116)

    def test_missing_days_count_as_zero(self):
        payload = copy.deepcopy(DOC_PAYLOAD)
        payload["historicalSales"] = [
            {"date": "2026-10-25", "quantity": 30},
            {"date": "2026-10-27", "quantity": 30},
        ]
        data = self.post(payload).json()["data"]
        self.assertEqual(data["historyDays"], 3)
        self.assertEqual(data["averageDailyDemand"], 20.0)  # (30 + 0 + 30) / 3

    def test_unsorted_history_is_handled(self):
        payload = copy.deepcopy(DOC_PAYLOAD)
        payload["historicalSales"].reverse()
        self.assertEqual(self.post(payload).json()["data"]["predictedDemand"], 116)

    def test_seasonal_method_on_long_history(self):
        payload = {**DOC_PAYLOAD, "historicalSales": long_history(28), "method": "seasonal_average"}
        data = self.post(payload).json()["data"]
        self.assertEqual(data["model"], "seasonal_average_v1")
        self.assertEqual(len(data["dailyForecast"]), 7)

    def test_seasonal_falls_back_on_short_history(self):
        payload = {**DOC_PAYLOAD, "method": "seasonal_average"}
        data = self.post(payload).json()["data"]
        self.assertEqual(data["model"], "moving_average_v1")
        self.assertTrue(any("seasonal_average needs" in w for w in data["warnings"]))

    def test_auto_method_explains_its_choice(self):
        payload = {**DOC_PAYLOAD, "historicalSales": long_history(35), "method": "auto"}
        data = self.post(payload).json()["data"]
        self.assertIn(data["model"], {"moving_average_v1", "seasonal_average_v1"})
        self.assertIn("selectionNote", data)

    def test_horizon_longer_than_a_week_works(self):
        payload = {**DOC_PAYLOAD, "historicalSales": long_history(28), "forecastDays": 30, "method": "seasonal_average"}
        data = self.post(payload).json()["data"]
        self.assertEqual(len(data["dailyForecast"]), 30)

    def test_zero_sales_history_gives_zero_forecast(self):
        payload = {**DOC_PAYLOAD, "historicalSales": [{"date": "2026-10-25", "quantity": 0}]}
        self.assertEqual(self.post(payload).json()["data"]["predictedDemand"], 0)


@override_settings(SERVICE_API_KEY=KEY)
class ValidationTests(APISimpleTestCase):
    def post(self, payload):
        return self.client.post(URL, payload, format="json", HTTP_X_API_KEY=KEY)

    def assert_400(self, payload, field_fragment):
        response = self.post(payload)
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertTrue(
            any(field_fragment in e["field"] for e in body["errors"]),
            f"expected an error mentioning {field_fragment}, got {body['errors']}",
        )

    def test_missing_product_id(self):
        payload = copy.deepcopy(DOC_PAYLOAD)
        del payload["productId"]
        self.assert_400(payload, "productId")

    def test_forecast_days_zero(self):
        self.assert_400({**DOC_PAYLOAD, "forecastDays": 0}, "forecastDays")

    def test_forecast_days_too_large(self):
        self.assert_400({**DOC_PAYLOAD, "forecastDays": 91}, "forecastDays")

    def test_empty_history(self):
        self.assert_400({**DOC_PAYLOAD, "historicalSales": []}, "historicalSales")

    def test_negative_quantity(self):
        bad = {**DOC_PAYLOAD, "historicalSales": [{"date": "2026-10-25", "quantity": -1}]}
        self.assert_400(bad, "historicalSales[0].quantity")

    def test_bad_date(self):
        bad = {**DOC_PAYLOAD, "historicalSales": [{"date": "25/10/2026", "quantity": 4}]}
        self.assert_400(bad, "historicalSales[0].date")

    def test_non_numeric_quantity(self):
        bad = {**DOC_PAYLOAD, "historicalSales": [{"date": "2026-10-25", "quantity": "lots"}]}
        self.assert_400(bad, "quantity")

    def test_too_many_records(self):
        rows = [{"date": "2026-10-25", "quantity": 1}] * 731
        self.assert_400({**DOC_PAYLOAD, "historicalSales": rows}, "historicalSales")

    def test_invalid_method(self):
        self.assert_400({**DOC_PAYLOAD, "method": "magic"}, "method")

    def test_malformed_json_is_400_standard_shape(self):
        response = self.client.post(URL, "{not json", content_type="application/json", HTTP_X_API_KEY=KEY)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])


@override_settings(SERVICE_API_KEY=KEY)
class ErrorShapeTests(APISimpleTestCase):
    def test_unknown_route_is_standard_404(self):
        response = self.client.get("/api/v1/nope")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])

    def test_wrong_method_is_405(self):
        response = self.client.get(URL, HTTP_X_API_KEY=KEY)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(response.json()["success"])
