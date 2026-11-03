"""
Demand forecasting models.

Two simple, explainable baselines (no black box):

* moving_average_v1   - average of the last N days, projected forward.
* seasonal_average_v1 - average of the same weekday over the last few weeks
                        (captures weekly patterns such as busy Saturdays).
* auto                - back-tests both on the most recent weeks and keeps the
                        one with the lower error ("improve only if data supports it").
"""
import math
from dataclasses import dataclass, field
from datetime import timedelta

import numpy as np
from django.conf import settings

from .metrics import wape

MOVING_AVERAGE_MODEL = "moving_average_v1"
SEASONAL_AVERAGE_MODEL = "seasonal_average_v1"

SEASON_LENGTH = 7
SEASONAL_WEEKS = 4
SEASONAL_MIN_HISTORY = 14
AUTO_MIN_HISTORY = 28
BACKTEST_HOLDOUT = 7
AUTO_MAX_FOLDS = 3
RECOMMENDED_HISTORY = 14

MODEL_IDS = {
    "moving_average": MOVING_AVERAGE_MODEL,
    "seasonal_average": SEASONAL_AVERAGE_MODEL,
}


# --------------------------------------------------------------------------
# Core numeric models (operate on plain numpy arrays of daily quantities)
# --------------------------------------------------------------------------
def moving_average_values(values, horizon, window):
    used = min(window, len(values))
    level = float(np.mean(values[-used:]))
    return np.full(horizon, level)


def seasonal_average_values(values, horizon, weeks=SEASONAL_WEEKS):
    n = len(values)
    out = []
    for step in range(1, horizon + 1):
        k = math.ceil(step / SEASON_LENGTH)  # nearest past occurrence of this weekday
        picks = []
        while len(picks) < weeks:
            idx = (n - 1) + step - SEASON_LENGTH * k
            if idx < 0:
                break
            picks.append(values[idx])
            k += 1
        out.append(float(np.mean(picks)) if picks else float(np.mean(values)))
    return np.array(out)


def naive_last_day_values(values, horizon):
    """Reference baseline used only in evaluation: repeat the last day."""
    return np.full(horizon, float(values[-1]))


def _backtest_wape(values, fn, folds, holdout=BACKTEST_HOLDOUT):
    actual_all, pred_all = [], []
    n = len(values)
    for fold in range(folds):
        cutoff = n - holdout * (folds - fold)
        actual_all.append(values[cutoff:cutoff + holdout])
        pred_all.append(fn(values[:cutoff], holdout))
    return wape(np.concatenate(actual_all), np.concatenate(pred_all))


# --------------------------------------------------------------------------
# Method selection (shared by the API and the evaluation command)
# --------------------------------------------------------------------------
def forecast_values(method, values, horizon, window=None):
    """
    Returns (daily_values, resolved_method, note, warnings).
    Handles the 'auto' mode and falls back safely when history is too short.
    """
    window = window or settings.MOVING_AVERAGE_WINDOW
    n = len(values)
    warnings = []
    note = None
    resolved = method

    if method == "seasonal_average" and n < SEASONAL_MIN_HISTORY:
        resolved = "moving_average"
        warnings.append(
            f"seasonal_average needs at least {SEASONAL_MIN_HISTORY} days of history "
            f"(received {n}); moving_average was used instead."
        )

    if method == "auto":
        if n < AUTO_MIN_HISTORY:
            resolved = "moving_average"
            note = (
                f"auto needs at least {AUTO_MIN_HISTORY} days of history to compare models "
                f"(received {n}); moving_average was used."
            )
        else:
            folds = max(1, min(AUTO_MAX_FOLDS, (n - SEASONAL_MIN_HISTORY) // BACKTEST_HOLDOUT))
            ma_err = _backtest_wape(values, lambda t, h: moving_average_values(t, h, window), folds)
            sa_err = _backtest_wape(values, seasonal_average_values, folds)
            if ma_err is None or sa_err is None or sa_err >= ma_err:
                resolved = "moving_average"
            else:
                resolved = "seasonal_average"
            note = (
                "auto compared both models on the most recent weeks "
                f"(backtest WAPE: moving_average={_fmt(ma_err)}, seasonal_average={_fmt(sa_err)}) "
                f"and chose {resolved}."
            )

    if resolved == "seasonal_average":
        return seasonal_average_values(values, horizon), resolved, note, warnings
    return moving_average_values(values, horizon, window), "moving_average", note, warnings


def _fmt(value):
    return "n/a" if value is None else f"{value:.3f}"


# --------------------------------------------------------------------------
# Public entry point used by the API view
# --------------------------------------------------------------------------
@dataclass
class ForecastResult:
    model: str
    daily: list
    predicted_demand: int
    average_daily_demand: float
    history_days: int
    explanation: str
    selection_note: str = None
    warnings: list = field(default_factory=list)


def run_forecast(series, horizon, method="moving_average"):
    values = series.to_numpy(dtype=float)
    n = len(values)
    window = settings.MOVING_AVERAGE_WINDOW

    daily_values, resolved, note, warnings = forecast_values(method, values, horizon, window)

    if n < RECOMMENDED_HISTORY:
        warnings.append(
            f"Only {n} day(s) of history were provided; at least {RECOMMENDED_HISTORY} days "
            "give a more reliable forecast."
        )

    start = series.index[-1].date() + timedelta(days=1)
    daily = [
        {"date": (start + timedelta(days=i)).isoformat(), "quantity": round(float(v), 2)}
        for i, v in enumerate(daily_values)
    ]
    total = round(float(np.sum(daily_values)), 6)
    predicted = int(math.floor(total + 0.5))  # round half up

    if resolved == "seasonal_average":
        explanation = (
            f"For each future day, averaged the same weekday over up to the last "
            f"{SEASONAL_WEEKS} weeks, then summed {horizon} day(s)."
        )
    else:
        used = min(window, n)
        explanation = (
            f"Averaged the last {used} day(s) ({float(daily_values[0]):.2f} units/day) "
            f"and projected it over {horizon} day(s)."
        )

    return ForecastResult(
        model=MODEL_IDS[resolved],
        daily=daily,
        predicted_demand=predicted,
        average_daily_demand=round(total / horizon, 2),
        history_days=n,
        explanation=explanation,
        selection_note=note,
        warnings=warnings,
    )
