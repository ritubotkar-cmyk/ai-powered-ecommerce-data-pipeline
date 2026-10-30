
import os
import getpass
from pathlib import Path
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")


def get_database_credentials():
    username = os.environ.get("ECOMMERCE_DB_USER")
    password = os.environ.get("ECOMMERCE_DB_PASSWORD")

    if not username:
        username = input("PostgreSQL username: ")

    if password is None:
        password = getpass.getpass(
            "PostgreSQL password: "
        )

    return username, password
