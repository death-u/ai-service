import csv
import io
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import SimpleTestCase


class SyntheticDataTests(SimpleTestCase):
    def generate(self, directory, seed=1):
        path = Path(directory) / f"sales_{seed}.csv"
        call_command("generate_synthetic_data", "--days", "30", "--seed", str(seed), "--output", str(path), stdout=io.StringIO())
        return path

    def test_row_count_and_labelling(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = list(csv.DictReader(self.generate(tmp).open()))
        self.assertEqual(len(rows), 5 * 6 * 30)
        self.assertTrue(all(r["dataSource"] == "synthetic_demo" for r in rows))
        self.assertTrue(all(int(r["quantity"]) >= 0 for r in rows))

    def test_same_seed_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.generate(tmp, seed=7).read_text()
            b = self.generate(tmp, seed=7).read_text()
        self.assertEqual(a, b)
