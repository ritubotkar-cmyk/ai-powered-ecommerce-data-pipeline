
import json
import os
import socket
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "reports" / "sales_summary.json"

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

MODEL_NAME = "qwen2.5:3b"


def ask_sales_chatbot(question):

    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            "Sales report not found. Run the pipeline first."
        )

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        report = json.load(file)

    # Supply verified analytics as the chatbot's context.
    context = {
        "metrics": report["metrics"],
        "category_performance": report["category_performance"],
        "daily_sales": report["daily_sales"]
    }

    prompt = (
        "You are an AI sales analytics assistant.\n"
        "Answer questions using ONLY the supplied data.\n"
        "Never invent sales figures or dates.\n"
        "If the data cannot answer the question, say so.\n"
        "Delivered revenue includes only delivered orders.\n"
        "In-progress order value is NOT realized revenue.\n"
        "Keep the response concise.\n\n"
        "SALES DATA:\n"
        + json.dumps(context)
        + "\n\nUSER QUESTION:\n"
        + question
        + "\n\nANSWER:"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 180,
            "num_ctx": 4096
        }
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        raise RuntimeError(
            "Ollama HTTP error: {}".format(error.code)
        ) from error

    except (URLError, socket.timeout, TimeoutError) as error:
        raise RuntimeError(
            "Ollama is unavailable or taking too long. "
            "Try a shorter question."
        ) from error

    answer = result.get("response", "").strip()

    if not answer:
        raise RuntimeError("Ollama returned an empty answer.")

    return answer
