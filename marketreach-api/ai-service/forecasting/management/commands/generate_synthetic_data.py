"""
Generate a synthetic FMCG daily-sales dataset for demos and evaluation.

Every row is labelled dataSource=synthetic_demo. This is FAKE data.
"""
import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand

PRODUCTS = [
    ("product_001", "Tomato paste sachet", 26),
    ("product_002", "Seasoning cubes", 40),
    ("product_003", "Mayonnaise jar", 9),
    ("product_004", "Tomato paste tin", 14),
    ("product_005", "Spaghetti pack", 18),
]
RETAILERS = [
    ("retailer_001", 1.6),
    ("retailer_002", 1.2),
    ("retailer_003", 1.0),
    ("retailer_004", 0.8),
    ("retailer_005", 0.6),
    ("retailer_006", 1.0),
]
# Mon..Sun: markets are busiest on Fri/Sat, quiet on Sun
WEEKDAY_FACTORS = [0.90, 0.95, 1.00, 1.00, 1.20, 1.45, 0.80]


class Command(BaseCommand):
    help = "Generate synthetic daily sales history (demo data) as a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=180)
        parser.add_argument("--end-date", default="2026-10-30", help="Last date, YYYY-MM-DD")
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument(
            "--output", default=str(Path(settings.BASE_DIR) / "data" / "synthetic_sales.csv")
        )

    def handle(self, *args, **options):
        rng = np.random.default_rng(options["seed"])
        end = date.fromisoformat(options["end_date"])
        days = options["days"]
        start = end - timedelta(days=days - 1)
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)

        rows = 0
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "productId", "retailerId", "quantity", "dataSource"])
            for product_id, _, base in PRODUCTS:
                for retailer_id, size in RETAILERS:
                    trend = rng.uniform(-0.0005, 0.002)  # slow drift per day
                    for offset in range(days):
                        day = start + timedelta(days=offset)
                        mean = base * size * WEEKDAY_FACTORS[day.weekday()]
                        mean *= 1 + trend * offset
                        if day.day >= 25 or day.day <= 2:  # month-end salary bump
                            mean *= 1.15
                        if rng.random() < 0.01:  # occasional promotion
                            mean *= 1.8
                        quantity = int(rng.poisson(max(mean, 0.1)))
                        if rng.random() < 0.015:  # occasional stock-out day
                            quantity = 0
                        writer.writerow(
                            [day.isoformat(), product_id, retailer_id, quantity, "synthetic_demo"]
                        )
                        rows += 1

        self.stdout.write(self.style.SUCCESS(f"Wrote {rows} rows to {output} (SYNTHETIC DEMO DATA)"))
