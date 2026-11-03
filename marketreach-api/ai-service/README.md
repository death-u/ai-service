# MarketReach AI: Demand Forecasting Service

Python / Django microservice for **MarketReach AI** (SpellaHub Team 2, GBfoods Nigeria Hackathon 2026).

The Node.js backend sends a product's recent daily sales; this service answers with a
**predicted demand** for the next N days. It is **stateless**: no database, no users,
no business modules. Node owns all business data. This service only does the maths.

```
React Native app  ->  Node.js API (MongoDB)  ->  THIS SERVICE (Django)
                          sends sales history       returns prediction
```

---

## 1. What is inside

```
marketreach-ai-service/
├── manage.py
├── requirements.txt
├── Procfile                    # start command for Railway/Render
├── .env.example                # copy to .env (never commit .env)
├── config/                     # Django settings and URLs
├── forecasting/
│   ├── views.py                # /health and /predict-demand
│   ├── serializers.py          # request validation
│   ├── authentication.py       # X-API-Key service authentication
│   ├── exceptions.py           # standard error format
│   ├── services/
│   │   ├── forecast.py         # the forecasting models
│   │   ├── series.py           # cleans sales into a daily series
│   │   ├── metrics.py          # MAE and WAPE
│   │   └── evaluation.py       # hold-out back-test
│   ├── management/commands/    # generate_synthetic_data, evaluate_models, make_sample_payload
│   └── tests/                  # 40 automated tests
├── data/
│   ├── synthetic_sales.csv     # FAKE demo data (5 products x 6 retailers x 180 days)
│   └── sample_request.json     # ready-to-send request body
├── docs/
│   ├── API_CONTRACT.md         # give this to Developer 2
│   └── EVALUATION.md           # accuracy results
└── scripts/smoke_test.py       # checks a running service end to end
```

---

## 2. Setup (about 5 minutes)

**You need:** Python 3.10 or newer (`python --version`) and Git.

### Windows (PowerShell)

```powershell
cd marketreach-ai-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell refuses to activate the venv, run
`Set-ExecutionPolicy -Scope Process Bypass` once and try again.

### Git Bash / Mac / Linux

```bash
cd marketreach-ai-service
python -m venv venv
source venv/Scripts/activate      # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Fill in `.env`

Open `.env` and set real values:

```
DEBUG=True
DJANGO_SECRET_KEY=<any long random string>
SERVICE_API_KEY=<another long random string>
```

Generate random strings with:

```
python -c "import secrets; print(secrets.token_urlsafe(40))"
```

Run it twice (one per value). **Do not paste these keys in the WhatsApp group.**

### Start the service

```
python manage.py runserver
```

Open http://127.0.0.1:8000/api/v1/health. You should see:

```json
{ "success": true, "message": "MarketReach AI forecasting service is healthy",
  "data": { "service": "marketreach-ai-service", "timestamp": "..." } }
```

---

## 3. How to test it (do these in order)

### Test 1: Automated tests (40 tests, about 1 second)

```
python manage.py test
```

Expected ending: `Ran 40 tests ... OK`. They cover health, authentication, the exact example
from the team document (expects `116`), validation errors, the forecasting maths, the metrics
and the data generator.

### Test 2: Smoke test against the running service

Keep `runserver` running in one terminal. In a **second** terminal (venv activated):

```
python scripts/smoke_test.py http://127.0.0.1:8000 YOUR_SERVICE_API_KEY
```

Use the same `SERVICE_API_KEY` you put in `.env`. Expected: five `[PASS]` lines and
`ALL CHECKS PASSED`. The same script works on the deployed URL later.

### Test 3: Manual test in Postman

1. **Health:** `GET http://127.0.0.1:8000/api/v1/health`. Expect `200`.
2. **Prediction:** `POST http://127.0.0.1:8000/api/v1/predict-demand`
   - Headers: `Content-Type: application/json` and `X-API-Key: <your key>`
   - Body (raw JSON): paste the contents of `data/sample_request.json`
   - Expect `200` with `predictedDemand`, `model`, `dailyForecast`, `isDemonstration: true`.
3. **Security check:** remove the `X-API-Key` header and send again. Expect `401`.
4. **Validation check:** change `forecastDays` to `0`. Expect `400` with an `errors` list.

### Test 4: curl (Git Bash; in PowerShell use `curl.exe`)

```
curl -X POST http://127.0.0.1:8000/api/v1/predict-demand \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_SERVICE_API_KEY" \
  -d @data/sample_request.json
```

### Test 5: The document's own example

```
curl -X POST http://127.0.0.1:8000/api/v1/predict-demand \
  -H "Content-Type: application/json" -H "X-API-Key: YOUR_SERVICE_API_KEY" \
  -d '{"productId":"product_001","retailerId":"retailer_001","forecastDays":7,"historicalSales":[{"date":"2026-10-25","quantity":15},{"date":"2026-10-26","quantity":18}]}'
```

Expected `predictedDemand`: **116** (average 16.5 per day x 7 = 115.5, rounded up).

---

## 3b. Make your own demo data (optional)

```
python manage.py generate_synthetic_data --days 180 --seed 42
python manage.py make_sample_payload --product product_002 --retailer retailer_003 --history-days 28
python manage.py evaluate_models --write-report
```

The dataset is **fake**. Every row is labelled `synthetic_demo`, and forecasts built from it
are flagged `isDemonstration: true` with a disclaimer, as the team document requires.

---

## 4. How the forecasting works (for your pitch)

| Model | Idea | Best when |
|---|---|---|
| `moving_average_v1` | Average of the last 7 days, projected forward | Steady demand |
| `seasonal_average_v1` | Average of the same weekday over the last up to 4 weeks | Weekly patterns (busy Fri/Sat) |
| `auto` | Back-tests both on the latest weeks, keeps the better one | You want the service to decide |

**Evaluation** (rolling hold-out on the synthetic data, 30 series, 120 forecasts per model):

| Model | MAE (units/day) | Daily WAPE | 7-day total WAPE |
|---|---|---|---|
| naive_last_day (reference) | 8.07 | 30.5% | 21.9% |
| moving_average | 6.50 | 24.5% | 11.7% |
| seasonal_average | 5.14 | 19.4% | 8.5% |
| auto | 5.34 | 20.1% | 9.3% |

- **MAE** = average miss in units per day. **WAPE** = total miss divided by total real sales (lower is better).
- The simple models beat the "repeat yesterday" reference, so they add value.
- Honest note for judges: the data is synthetic, so real-world accuracy will differ.
  `auto` is slightly behind `seasonal_average` here because it picks from only a few recent weeks.
  That is a trade-off, not a bug.

**Known limitations** (say these out loud in the pitch, it builds trust):
- No awareness of promotions, price changes, holidays or stock-outs unless they appear in recent sales.
- Missing days are treated as zero sales.
- Short history (under 14 days) gives a rough estimate, and the response says so in `warnings`.
- Forecasts are totals for a product at one retailer, not a full supply-chain plan.

---

## 5. Deploy on Railway

1. Create an **empty GitHub repo** named `marketreach-ai-service` (see section 6) and push this code.
2. On https://railway.app: **New Project -> Deploy from GitHub repo** and choose it.
3. Open the service -> **Variables** and add:

   | Variable | Value |
   |---|---|
   | `DEBUG` | `False` |
   | `DJANGO_SECRET_KEY` | a new random string |
   | `SERVICE_API_KEY` | a new random string (give it to Developer 2 privately) |
   | `ALLOWED_HOSTS` | `localhost,127.0.0.1,.up.railway.app` |

4. **Settings -> Networking -> Generate Domain.**
5. Check `https://<your-domain>/api/v1/health`, then run:
   `python scripts/smoke_test.py https://<your-domain> <SERVICE_API_KEY>`

The `Procfile` already tells Railway how to start the service. No database is needed.
Render works the same way (start command: `gunicorn config.wsgi`).

---

## 6. GitHub workflow (from the team rules)

This service lives in **its own repo**, `marketreach-ai-service`, separate from the Node repo.
Ask the team lead whether they create the repo or you do.

```
git init
git add .
git commit -m "chore(ai): initialize Django forecasting microservice"
git branch -M main
git remote add origin https://github.com/<owner>/marketreach-ai-service.git
git push -u origin main
```

After that, work on branches and open Pull Requests:

```
git switch -c feature/ai-forecasting-service
git commit -m "feat(ai): implement demand prediction API"
git push -u origin feature/ai-forecasting-service
```

Never commit `.env`. It is already in `.gitignore`.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the venv and run `pip install -r requirements.txt` |
| `ImproperlyConfigured: DJANGO_SECRET_KEY` | Create `.env` (copy `.env.example`), or set `DEBUG=True` locally |
| `401` on `/predict-demand` | `X-API-Key` header missing or different from `SERVICE_API_KEY` in `.env` |
| `400 Bad Request` on every call in production | Add your domain to `ALLOWED_HOSTS` |
| Port 8000 busy | `python manage.py runserver 8001` |
| Changed `.env` but nothing changed | Stop and restart the server |
| `pip install` is slow or fails on pandas | Retry on a stable connection, or use Python 3.11/3.12 |

---

## 8. Definition of done (Developer 3)

- [x] Independent Django project with requirements, `.env.example` and README
- [x] `GET /api/v1/health` and `POST /api/v1/predict-demand`
- [x] Synthetic FMCG daily sales dataset, labelled as demo data
- [x] Moving-average baseline, plus a seasonal model and `auto` selection
- [x] Hold-out evaluation with MAE and WAPE, limitations documented
- [x] Service authentication, payload validation, safe error handling
- [x] Request/response contract in `docs/API_CONTRACT.md`
- [ ] Deployed and tested together with Developer 2 (your job on Days 4 and 5)
