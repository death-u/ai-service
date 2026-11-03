"""Back-test the forecasting models on the synthetic dataset and print MAE / WAPE."""
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from forecasting.services.evaluation import evaluate_dataframe


def _pct(value):
    return "n/a" if value is None else f"{value * 100:.1f}%"


class Command(BaseCommand):
    help = "Evaluate forecasting models with a rolling hold-out back-test."

    def add_arguments(self, parser):
        parser.add_argument("--data", default=str(Path(settings.BASE_DIR) / "data" / "synthetic_sales.csv"))
        parser.add_argument("--holdout", type=int, default=7)
        parser.add_argument("--folds", type=int, default=4)
        parser.add_argument("--write-report", action="store_true", help="Write docs/EVALUATION.md")

    def handle(self, *args, **options):
        path = Path(options["data"])
        if not path.exists():
            raise CommandError(f"{path} not found. Run: python manage.py generate_synthetic_data")

        frame = pd.read_csv(path)
        report = evaluate_dataframe(frame, holdout=options["holdout"], folds=options["folds"])

        lines = [
            "# Forecast evaluation (synthetic demo data)",
            "",
            f"- Series evaluated: {report['series_evaluated']} (product x retailer)",
            f"- Method: rolling-origin hold-out, {report['folds']} folds x {report['holdout_days']} days each",
            f"- Forecasts per method: {report['forecasts_per_method']}",
            "",
            "| Model | MAE (units/day) | Daily WAPE | 7-day total WAPE |",
            "|---|---|---|---|",
        ]
        for method, metrics in report["results"].items():
            mae_text = "n/a" if metrics["mae"] is None else f"{metrics['mae']:.2f}"
            lines.append(
                f"| {method} | {mae_text} | {_pct(metrics['wape'])} | {_pct(metrics['weekly_total_wape'])} |"
            )
        lines += [
            "",
            f"`auto` chose: {report['auto_choices']}",
            "",
            "MAE = average miss in units per day. WAPE = total absolute miss divided by total real sales "
            "(lower is better). `naive_last_day` is a trivial reference to prove the real models add value.",
            "",
            "**Limitations:** the data is synthetic, so real-world accuracy will differ. The models are "
            "simple baselines: they do not know about promotions, price changes, holidays or stock-outs "
            "unless those show up in the recent sales history.",
        ]
        text = "\n".join(lines)
        self.stdout.write(text)

        if options["write_report"]:
            out = Path(settings.BASE_DIR) / "docs" / "EVALUATION.md"
            out.parent.mkdir(exist_ok=True)
            out.write_text(text + "\n", encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"\nSaved {out}"))
