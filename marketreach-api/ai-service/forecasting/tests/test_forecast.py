import numpy as np
from django.test import SimpleTestCase

from forecasting.services.forecast import (
    forecast_values,
    moving_average_values,
    seasonal_average_values,
)
from forecasting.services.metrics import mae, wape
from forecasting.services.series import build_daily_series


class MetricTests(SimpleTestCase):
    def test_mae(self):
        self.assertAlmostEqual(mae([10, 20], [12, 17]), 2.5)

    def test_wape(self):
        self.assertAlmostEqual(wape([10, 20], [12, 17]), 5 / 30)

    def test_wape_is_none_when_no_sales(self):
        self.assertIsNone(wape([0, 0], [1, 1]))

    def test_perfect_forecast(self):
        self.assertEqual(mae([5, 5], [5, 5]), 0.0)
        self.assertEqual(wape([5, 5], [5, 5]), 0.0)


class ModelTests(SimpleTestCase):
    def test_moving_average_uses_last_window(self):
        values = np.array([100.0, 100.0, 1, 2, 3, 4, 5, 6, 7])
        result = moving_average_values(values, 3, window=7)
        np.testing.assert_allclose(result, [np.mean([2, 3, 4, 5, 6, 7, 1][-7:])] * 3, rtol=0)

    def test_moving_average_short_history_uses_all(self):
        np.testing.assert_allclose(moving_average_values(np.array([15.0, 18.0]), 2, 7), [16.5, 16.5])

    def test_seasonal_average_repeats_weekly_pattern(self):
        week = [10, 12, 14, 16, 30, 40, 8]
        values = np.array(week * 4, dtype=float)
        result = seasonal_average_values(values, 7)
        np.testing.assert_allclose(result, week)

    def test_seasonal_average_beyond_one_week(self):
        week = [10, 12, 14, 16, 30, 40, 8]
        values = np.array(week * 4, dtype=float)
        result = seasonal_average_values(values, 14)
        np.testing.assert_allclose(result, week * 2)

    def test_auto_prefers_seasonal_when_pattern_is_strong(self):
        week = [10, 12, 14, 16, 30, 40, 8]
        values = np.array(week * 6, dtype=float)
        _, resolved, note, _ = forecast_values("auto", values, 7)
        self.assertEqual(resolved, "seasonal_average")
        self.assertIn("chose seasonal_average", note)

    def test_auto_uses_moving_average_when_history_short(self):
        _, resolved, note, _ = forecast_values("auto", np.arange(10, dtype=float), 7)
        self.assertEqual(resolved, "moving_average")
        self.assertIn("at least 28", note)


class SeriesTests(SimpleTestCase):
    def test_gap_filling_and_summing(self):
        series = build_daily_series(
            [
                {"date": "2026-10-01", "quantity": 4},
                {"date": "2026-10-01", "quantity": 6},
                {"date": "2026-10-04", "quantity": 5},
            ]
        )
        self.assertEqual(list(series.values), [10.0, 0.0, 0.0, 5.0])
