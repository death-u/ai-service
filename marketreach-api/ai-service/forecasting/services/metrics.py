"""Forecast accuracy metrics."""
import numpy as np


def mae(actual, predicted):
    """Mean Absolute Error: the average size of the miss, in units sold per day."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if actual.size == 0:
        return None
    return float(np.mean(np.abs(actual - predicted)))


def wape(actual, predicted):
    """
    Weighted Absolute Percentage Error: total absolute miss / total actual sales.
    0.20 means "off by 20% of what was really sold". Returns None when there
    were no sales at all (the ratio is undefined).
    """
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    total_actual = float(np.sum(np.abs(actual)))
    if total_actual == 0:
        return None
    return float(np.sum(np.abs(actual - predicted)) / total_actual)
