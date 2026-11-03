"""Turn a list of {date, quantity} records into a clean daily time series."""
import pandas as pd


def build_daily_series(points):
    """
    - Several records on the same date are summed.
    - Days with no record between the first and last date are filled with 0
      (assumption: no record = nothing sold that day).
    Returns a pandas Series indexed by consecutive days.
    """
    frame = pd.DataFrame(list(points))
    frame["date"] = pd.to_datetime(frame["date"])
    daily = frame.groupby("date")["quantity"].sum().sort_index()
    full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    return daily.reindex(full_range, fill_value=0.0).astype(float)
