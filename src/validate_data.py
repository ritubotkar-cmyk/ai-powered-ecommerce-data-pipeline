
import csv
from pathlib import Path
from datetime import date
from decimal import Decimal, InvalidOperation


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "orders.csv"
)

REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "product",
    "category",
    "quantity",
    "unit_price",
    "discount",
    "status",
    "city",
]

VALID_STATUSES = {
    "DELIVERED",
    "SHIPPED",
    "CANCELLED",
    "PROCESSING",
}


def validate_data(file_path=DATA_FILE):
    print("Starting data quality validation...")

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    with file_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header")

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        rows = list(reader)

    if not rows:
        raise ValueError("CSV contains no order records")

    order_ids = set()

    for row_number, row in enumerate(rows, start=2):
        order_id = row["order_id"].strip()

        # 1. Required values
        for column in REQUIRED_COLUMNS:
            if not row[column].strip():
                raise ValueError(
                    f"Row {row_number}: {column} is empty"
                )

        # 2. Unique order IDs
        if order_id in order_ids:
            raise ValueError(
                f"Row {row_number}: duplicate order_id "
                f"{order_id}"
            )

        order_ids.add(order_id)

        # 3. Valid dates
        try:
            order_date = date.fromisoformat(
                row["order_date"]
            )
        except ValueError as exc:
            raise ValueError(
                f"Row {row_number}: invalid order_date"
            ) from exc

        # 4. Numeric and business-rule checks
        try:
            quantity = int(row["quantity"])
            unit_price = Decimal(row["unit_price"])
            discount = Decimal(row["discount"])
        except (ValueError, InvalidOperation) as exc:
            raise ValueError(
                f"Row {row_number}: invalid numeric value"
            ) from exc

        if quantity <= 0:
            raise ValueError(
                f"Row {row_number}: quantity must be positive"
            )

        if not unit_price.is_finite() or unit_price <= 0:
            raise ValueError(
                f"Row {row_number}: unit_price must be positive"
            )

        if (
            not discount.is_finite()
            or discount < 0
            or discount > 1
        ):
            raise ValueError(
                f"Row {row_number}: discount must be "
                "between 0 and 1"
            )

        # 5. Valid order status
        if row["status"] not in VALID_STATUSES:
            raise ValueError(
                f"Row {row_number}: invalid status "
                f"{row['status']}"
            )

    print("Data quality validation successful.")
    print(f"Total records validated: {len(rows)}")
    print("Null and empty-value checks: PASSED")
    print("Duplicate order ID checks: PASSED")
    print("Date and numeric checks: PASSED")
    print("Business-rule checks: PASSED")

    return True


if __name__ == "__main__":
    validate_data()
