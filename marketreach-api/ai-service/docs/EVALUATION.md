# Forecast evaluation (synthetic demo data)

- Series evaluated: 30 (product x retailer)
- Method: rolling-origin hold-out, 4 folds x 7 days each
- Forecasts per method: 120

| Model | MAE (units/day) | Daily WAPE | 7-day total WAPE |
|---|---|---|---|
| naive_last_day | 8.07 | 30.5% | 21.9% |
| moving_average | 6.50 | 24.5% | 11.7% |
| seasonal_average | 5.14 | 19.4% | 8.5% |
| auto | 5.34 | 20.1% | 9.3% |

`auto` chose: {'moving_average': 16, 'seasonal_average': 104}

MAE = average miss in units per day. WAPE = total absolute miss divided by total real sales (lower is better). `naive_last_day` is a trivial reference to prove the real models add value.

**Limitations:** the data is synthetic, so real-world accuracy will differ. The models are simple baselines: they do not know about promotions, price changes, holidays or stock-outs unless those show up in the recent sales history.
