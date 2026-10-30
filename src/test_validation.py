
import csv
import unittest
from pathlib import Path

from validate_data import validate_data


class TestDataValidation(unittest.TestCase):

    def test_duplicate_order_detection(self):
        project_dir = Path(__file__).resolve().parent.parent

        source = project_dir / "data" / "orders.csv"
        bad = project_dir / "data" / "orders_invalid_test.csv"

        try:
            with source.open(
                "r", encoding="utf-8", newline=""
            ) as file:
                rows = list(csv.reader(file))

            # Add a duplicate of the first data row
            rows.append(rows[1])

            with bad.open(
                "w", encoding="utf-8", newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerows(rows)

            # Expect validation to reject the duplicate
            with self.assertRaisesRegex(
                ValueError, "duplicate order_id"
            ):
                validate_data(bad)

        finally:
            if bad.exists():
                bad.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
