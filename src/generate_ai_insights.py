import os
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


PROJECT_DIR = Path(__file__).resolve().parent.parent

REPORT_FILE = PROJECT_DIR / "reports" / "sales_summary.json"
OUTPUT_FILE = PROJECT_DIR / "reports" / "ai_insights.txt"

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)
MODEL_NAME = "qwen2.5:3b"


def generate_ai_insights():
    # Step 1: Check that the sales report exists.
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            "Sales report not found. "
            "Run generate_sales_report.py first."
        )

    # Step 2: Read the verified metrics.
    with REPORT_FILE.open("r", encoding="utf-8") as file:
        report = json.load(file)

    # Send aggregate metrics, not individual customer records.
    
    metrics = report["metrics"]
    categories = report["category_performance"]

    summary = {
    "total_orders": metrics["total_orders"],
    "delivered_orders": metrics["delivered_orders"],
    "cancelled_orders": metrics["cancelled_orders"],
    "in_progress_orders": metrics["in_progress_orders"],
    "delivered_revenue": metrics["delivered_revenue"],
    "in_progress_order_value": metrics["in_progress_order_value"],
    "categories": categories
    }

    prompt = (
    "You are an e-commerce sales analyst.\n"
    "Use ONLY the supplied data.\n"
    "Write exactly 4 short bullet points covering:\n"
    "1. Delivered revenue.\n"
    "2. Best-performing category.\n"
    "3. Cancelled and in-progress orders.\n"
    "4. One practical business recommendation.\n"
    "Do not invent numbers.\n"
    "Do not treat in-progress value as revenue.\n\n"
    "Sales data:\n"
    + json.dumps(summary)
)

    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 250,
        "num_ctx": 2048
        }
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # Step 3: Ask the local model to generate insights.
    try:
        with urlopen(request, timeout=300) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        raise RuntimeError(
            f"Ollama returned HTTP error {error.code}. "
            "Check the model name and Ollama installation."
        ) from error

    except URLError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama "
            "is installed and running."
        ) from error

    insights = result.get("response", "").strip()

    if not insights:
        raise RuntimeError(
            "The AI model returned an empty response."
        )

    # Step 4: Save the generated report.
    OUTPUT_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        file.write(insights + "\n")

    print("AI insights generated successfully.")
    print(f"Report location: {OUTPUT_FILE}")
    print("\nAI-generated report:\n")
    print(insights)


if __name__ == "__main__":
    generate_ai_insights()
