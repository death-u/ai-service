# API Contract: MarketReach AI Forecasting Service

Base URL (local): `http://127.0.0.1:8000`  
Base URL (deployed): `https://<your-service>.up.railway.app`  
Version prefix: `/api/v1`

All responses are JSON and follow the same shape as the Node.js API:

```json
{ "success": true,  "message": "...", "data": { } }
{ "success": false, "message": "...", "errors": [ { "field": "body.forecastDays", "message": "..." } ] }
```

## Authentication

`POST` endpoints require the shared secret in a header:

```
X-API-Key: <SERVICE_API_KEY>
```

Missing or wrong key: `401`. `/health` is public.

---

## GET /api/v1/health

```json
{
  "success": true,
  "message": "MarketReach AI forecasting service is healthy",
  "data": { "service": "marketreach-ai-service", "timestamp": "2026-10-31T10:00:00Z" }
}
```

---

## POST /api/v1/predict-demand

### Request

```json
{
  "productId": "product_001",
  "retailerId": "retailer_001",
  "forecastDays": 7,
  "historicalSales": [
    { "date": "2026-10-25", "quantity": 15 },
    { "date": "2026-10-26", "quantity": 18 }
  ]
}
```

| Field | Required | Rules |
|---|---|---|
| `productId` | yes | non-empty string, max 100 chars |
| `retailerId` | yes | non-empty string, max 100 chars |
| `forecastDays` | yes | integer 1 to 90 |
| `historicalSales` | yes | 1 to 730 records, each `{ date: "YYYY-MM-DD", quantity: number >= 0 }` |
| `method` | no | `moving_average` (default), `seasonal_average`, or `auto` |
| `dataSource` | no | `historical_sales` (default) or `synthetic_demo` |

Data handling rules:
- Records may be in any order.
- Several records on the same date are **summed**.
- Days missing between the first and last date count as **0 units sold**.
- Send **14+ days** of history (28+ is better). Fewer days still works, with a warning.
- Do not send personal information (names, phone numbers). Only IDs, dates and quantities are needed.

### Success response (200)

```json
{
  "success": true,
  "message": "Demand forecast generated successfully",
  "data": {
    "productId": "product_001",
    "retailerId": "retailer_001",
    "forecastDays": 7,
    "predictedDemand": 116,
    "model": "moving_average_v1",
    "dataSource": "historical_sales",
    "generatedAt": "2026-10-31T10:00:00Z",

    "averageDailyDemand": 16.5,
    "historyDays": 2,
    "dailyForecast": [ { "date": "2026-10-27", "quantity": 16.5 } ],
    "explanation": "Averaged the last 2 day(s) (16.50 units/day) and projected it over 7 day(s).",
    "isDemonstration": false,
    "warnings": [ "Only 2 day(s) of history were provided; ..." ]
  }
}
```

The first seven fields (`productId` to `generatedAt`) are exactly the contract from the team document.
The remaining fields are **additive extras**. Node can store or ignore them.
When `dataSource` is `synthetic_demo`, the response also has `"isDemonstration": true` and a `disclaimer`.
When `method` is `auto`, a `selectionNote` explains which model was chosen and why.

`predictedDemand` is the **total** units expected over the next `forecastDays` days (rounded half up).

### Models

| `model` value | What it does |
|---|---|
| `moving_average_v1` | Average of the last 7 days, projected forward |
| `seasonal_average_v1` | Average of the same weekday over the last up to 4 weeks (needs 14+ days) |

### Errors

| Status | When |
|---|---|
| 400 | Invalid payload (see `errors[]`), malformed JSON |
| 401 | Missing or invalid `X-API-Key` |
| 404 | Unknown route |
| 405 | Wrong HTTP method |
| 415 | Body is not `application/json` |
| 500 | Unexpected error (details are logged server-side, not returned) |

---

## Calling the service from Node.js (for Developer 2)

Environment variables on the Node side:

```
FORECAST_SERVICE_URL=https://<your-service>.up.railway.app
FORECAST_SERVICE_API_KEY=<same value as SERVICE_API_KEY>
```

```js
// src/modules/forecasts/services/forecastClient.js
export async function requestDemandForecast({ productId, retailerId, forecastDays, historicalSales }) {
  try {
    const response = await fetch(`${process.env.FORECAST_SERVICE_URL}/api/v1/predict-demand`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.FORECAST_SERVICE_API_KEY,
      },
      body: JSON.stringify({ productId, retailerId, forecastDays, historicalSales }),
      signal: AbortSignal.timeout(10_000), // never wait forever
    });

    const body = await response.json();
    if (!response.ok || !body.success) {
      throw new Error(body.message || `Forecast service error (${response.status})`);
    }
    return body.data;
  } catch (error) {
    // Handle gracefully: the mobile app should still work without a forecast.
    return null;
  }
}
```

## Things to confirm with Developer 2 on Day 1

1. Is the request/response shape above final? (The team document marks the response as illustrative.)
2. Which `method` should Node send? Suggested: `auto`.
3. Who generates the shared `SERVICE_API_KEY`, and how is it shared safely (not in the group chat)?
4. Which `dataSource` value to send while the Node database only holds demo data? (`synthetic_demo`)
