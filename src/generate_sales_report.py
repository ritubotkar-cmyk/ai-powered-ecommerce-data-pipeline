
import json
import os
from datetime import date, datetime
from decimal import Decimal
from getpass import getpass
from pathlib import Path
from db_credentials import get_database_credentials
import psycopg2
from psycopg2.extras import RealDictCursor


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "reports" / "sales_summary.json"


def json_value(value):
    """Convert database values into JSON-compatible values."""
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def generate_sales_report():
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

        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            # 1. Overall sales metrics
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_orders,

                    COUNT(*) FILTER (
                        WHERE status = 'DELIVERED'
                    ) AS delivered_orders,

                    COUNT(*) FILTER (
                        WHERE status = 'CANCELLED'
                    ) AS cancelled_orders,

                    COUNT(*) FILTER (
                        WHERE status IN (
                            'PROCESSING', 'SHIPPED'
                        )
                    ) AS in_progress_orders,

                    COALESCE(
                        SUM(
                            quantity * unit_price
                            * (1 - discount)
                        ) FILTER (
                            WHERE status = 'DELIVERED'
                        ),
                        0
                    ) AS delivered_revenue,

                    COALESCE(
                        SUM(
                            quantity * unit_price
                            * (1 - discount)
                        ) FILTER (
                            WHERE status IN (
                                'PROCESSING', 'SHIPPED'
                            )
                        ),
                        0
                    ) AS in_progress_order_value

                FROM raw_orders;
            """)

            metrics = dict(cursor.fetchone())

            # 2. Revenue by product category
            cursor.execute("""
                SELECT
                    category,
                    COUNT(*) AS order_count,
                    COALESCE(
                        SUM(
                            quantity * unit_price
                            * (1 - discount)
                        ) FILTER (
                            WHERE status = 'DELIVERED'
                        ),
                        0
                    ) AS delivered_revenue
                FROM raw_orders
                WHERE status <> 'CANCELLED'
                GROUP BY category
                ORDER BY delivered_revenue DESC;
            """)

            category_rows = [
                dict(row) for row in cursor.fetchall()
            ]

            # 3. Daily delivered revenue
            cursor.execute("""
                SELECT
                    order_date,
                    COUNT(*) AS delivered_orders,
                    SUM(
                        quantity * unit_price
                        * (1 - discount)
                    ) AS delivered_revenue
                FROM raw_orders
                WHERE status = 'DELIVERED'
                GROUP BY order_date
                ORDER BY order_date;
            """)

            daily_rows = [
                dict(row) for row in cursor.fetchall()
            ]

        # Convert database values into JSON-safe values.
        report = {
            "generated_at": datetime.now().isoformat(),
            "source_table": "public.raw_orders",
            "metrics": {
                key: json_value(value)
                for key, value in metrics.items()
            },
            "category_performance": [
                {
                    key: json_value(value)
                    for key, value in row.items()
                }
                for row in category_rows
            ],
            "daily_sales": [
                {
                    key: json_value(value)
                    for key, value in row.items()
                }
                for row in daily_rows
            ],
        }

        REPORT_FILE.parent.mkdir(
            parents=True, exist_ok=True
        )

        with REPORT_FILE.open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(
                report, file, indent=4, ensure_ascii=False
            )

        print("\nSales report generated successfully.")
        print(f"Report location: {REPORT_FILE}")
        print("\nOverall metrics:")

        for key, value in report["metrics"].items():
            print(f"{key}: {value}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    generate_sales_report()
