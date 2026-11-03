"""
Hold-out evaluation (rolling-origin back-test).

For every product/retailer series we repeatedly hide the last few days,
forecast them from what came before, and compare with what really happened.
"""
import numpy as np

from .forecast import (
    BACKTEST_HOLDOUT,
    SEASONAL_MIN_HISTORY,
    forecast_values,
    naive_last_day_values,
)
from .metrics import mae, wape
from .series import build_daily_series

METHODS = ["naive_last_day", "moving_average", "seasonal_average", "auto"]


def evaluate_dataframe(frame, holdout=BACKTEST_HOLDOUT, folds=4, window=7):
    totals = {m: {"actual": [], "pred": [], "wk_actual": [], "wk_pred": []} for m in METHODS}
    auto_choices = {"moving_average": 0, "seasonal_average": 0}
    series_count = 0

    for _, group in frame.groupby(["productId", "retailerId"]):
        values = build_daily_series(group[["date", "quantity"]].to_dict("records")).to_numpy(float)
        if len(values) < SEASONAL_MIN_HISTORY + holdout * folds:
            continue
        series_count += 1

        for fold in range(folds):
            cutoff = len(values) - holdout * (folds - fold)
            train = values[:cutoff]
            actual = values[cutoff:cutoff + holdout]

            for method in METHODS:
                if method == "naive_last_day":
                    pred = naive_last_day_values(train, holdout)
                else:
                    pred, resolved, _, _ = forecast_values(method, train, holdout, window)
                    if method == "auto":
                        auto_choices[resolved] += 1
                bucket = totals[method]
                bucket["actual"].append(actual)
                bucket["pred"].append(pred)
                bucket["wk_actual"].append(actual.sum())
                bucket["wk_pred"].append(pred.sum())

    results = {}
    for method, bucket in totals.items():
        actual = np.concatenate(bucket["actual"])
        pred = np.concatenate(bucket["pred"])
        results[method] = {
            "mae": mae(actual, pred),
            "wape": wape(actual, pred),
            "weekly_total_wape": wape(bucket["wk_actual"], bucket["wk_pred"]),
        }
    return {
        "series_evaluated": series_count,
        "holdout_days": holdout,
        "folds": folds,
        "forecasts_per_method": series_count * folds,
        "results": results,
        "auto_choices": auto_choices,
    }
