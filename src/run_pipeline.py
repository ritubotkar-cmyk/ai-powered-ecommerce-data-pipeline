
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "pipeline.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def run_step(step_name, script_name):
    script_path = PROJECT_DIR / "src" / script_name

    if not script_path.exists():
        raise FileNotFoundError(
            f"Required script not found: {script_path}"
        )

    logger.info("STARTED: %s", step_name)

    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_DIR),
            check=True,
        )
    except subprocess.CalledProcessError as error:
        logger.error(
            "FAILED: %s (exit code %s)",
            step_name,
            error.returncode,
        )
        raise

    logger.info("SUCCEEDED: %s", step_name)


def main():
    start_time = datetime.now()

    logger.info("========== PIPELINE STARTED ==========")

    steps = [
        ("Load and validate orders", "load_to_postgres.py"),
        ("Generate sales report", "generate_sales_report.py"),
        ("Generate AI insights", "generate_ai_insights.py"),
    ]

    try:
        for step_name, script_name in steps:
            run_step(step_name, script_name)

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(
            "========== PIPELINE SUCCEEDED in %.2f seconds ==========",
            duration,
        )

    except Exception:
        logger.exception("PIPELINE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
