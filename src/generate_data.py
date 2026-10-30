
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "orders.csv"
)

products = [
    ("Laptop", "Electronics", 55000),
    ("Headphones", "Electronics", 2500),
    ("Keyboard", "Accessories", 1200),
    ("Office Chair", "Furniture", 8500),
    ("Notebook", "Stationery", 100),
    ("Monitor", "Electronics", 12000),
]

cities = ["Pune", "Mumbai", "Delhi", "Bengaluru", "Hyderabad"]
statuses = ["DELIVERED", "SHIPPED", "CANCELLED", "PROCESSING"]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
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
    ])

    start_date = date(2026, 1, 1)

    for i in range(1, 101):
        product, category, unit_price = random.choice(products)
        order_date = start_date + timedelta(
            days=random.randint(0, 89)
        )
        quantity = random.randint(1, 5)
        discount = random.choice([0, 0, 0.05, 0.10, 0.15])

        writer.writerow([
            f"ORD{i:04d}",
            f"CUST{random.randint(1, 40):03d}",
            order_date.isoformat(),
            product,
            category,
            quantity,
            unit_price,
            discount,
            random.choice(statuses),
            random.choice(cities),
        ])

print(f"Dataset generated: {OUTPUT_FILE}")
print("Total orders created: 100")
