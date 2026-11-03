"""Build a ready-to-send /predict-demand request body from the synthetic dataset."""
import json
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a sample request JSON for POST /api/v1/predict-demand."

    def add_arguments(self, parser):
        parser.add_argument("--product", default="product_001")
        parser.add_argument("--retailer", default="retailer_001")
        parser.add_argument("--history-days", type=int, default=28)
        parser.add_argument("--forecast-days", type=int, default=7)
        parser.add_argument("--method", default="auto", choices=["moving_average", "seasonal_average", "auto"])
        parser.add_argument("--data", default=str(Path(settings.BASE_DIR) / "data" / "synthetic_sales.csv"))
        parser.add_argument("--output", default=str(Path(settings.BASE_DIR) / "data" / "sample_request.json"))

    def handle(self, *args, **options):
        path = Path(options["data"])
        if not path.exists():
            raise CommandError(f"{path} not found. Run: python manage.py generate_synthetic_data")

        frame = pd.read_csv(path)
        subset = frame[(frame["productId"] == options["product"]) & (frame["retailerId"] == options["retailer"])]
        if subset.empty:
            raise CommandError("No rows for that product/retailer combination.")
        subset = subset.sort_values("date").tail(options["history_days"])

        payload = {
            "productId": options["product"],
            "retailerId": options["retailer"],
            "forecastDays": options["forecast_days"],
            "method": options["method"],
            "dataSource": "synthetic_demo",
            "historicalSales": [
                {"date": row.date, "quantity": int(row.quantity)} for row in subset.itertuples()
            ],
        }
        out = Path(options["output"])
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote {out} ({len(payload['historicalSales'])} days of history)"))
