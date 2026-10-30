
import csv
import os
from pathlib import Path
from getpass import getpass
from db_credentials import get_database_credentials
import psycopg2
from psycopg2.extras import execute_values

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "orders.csv"


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {DATA_FILE}")

    # Revalidate the source before loading
    from validate_data import validate_data
    validate_data(DATA_FILE)

    username, password = get_database_credentials()

    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("ECOMMERCE_DB_HOST", "localhost"),
            port=int(os.getenv("ECOMMERCE_DB_PORT", "5432")),
            dbname="ecommerce_analytics",
            user=username,
            password=password,
        )

        with DATA_FILE.open(
            "r", encoding="utf-8", newline=""
        ) as file:
            reader = csv.DictReader(file)
            rows = [
                (
                    row["order_id"],
                    row["customer_id"],
                    row["order_date"],
                    row["product"],
                    row["category"],
                    int(row["quantity"]),
                    row["unit_price"],
                    row["discount"],
                    row["status"],
                    row["city"],
                )
                for row in reader
            ]

        sql = """
            INSERT INTO raw_orders (
                order_id, customer_id, order_date,
                product, category, quantity, unit_price,
                discount, status, city
            )
            VALUES %s
            ON CONFLICT (order_id)
            DO UPDATE SET
                customer_id = EXCLUDED.customer_id,
                order_date = EXCLUDED.order_date,
                product = EXCLUDED.product,
                category = EXCLUDED.category,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price,
                discount = EXCLUDED.discount,
                status = EXCLUDED.status,
                city = EXCLUDED.city,
                loaded_at = CURRENT_TIMESTAMP
        """

        with connection:
            with connection.cursor() as cursor:
                execute_values(cursor, sql, rows)

        print(f"Successfully processed {len(rows)} records.")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    load_data()
