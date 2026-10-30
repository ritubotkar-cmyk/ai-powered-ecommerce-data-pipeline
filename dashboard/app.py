
import json
from pathlib import Path
import os
import subprocess
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# -------------------------------------------------
# 1. Project paths
# -------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

SRC_DIR = PROJECT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from chatbot import ask_sales_chatbot

SALES_REPORT = PROJECT_DIR / "reports" / "sales_summary.json"
AI_REPORT = PROJECT_DIR / "reports" / "ai_insights.txt"


# -------------------------------------------------
# 2. Dashboard configuration
# -------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 E-Commerce Sales Analytics")
st.caption("Python | PostgreSQL | SQL | Streamlit | Ollama AI")

st.subheader("Pipeline Controls")

if st.button("Run Pipeline & Refresh Dashboard"):

    if not os.environ.get("ECOMMERCE_DB_USER") or (
        os.environ.get("ECOMMERCE_DB_PASSWORD") is None
    ):
        st.error(
            "Database credentials are not configured. "
            "Start Streamlit from a Command Prompt "
            "with the database environment variables set."
        )
        st.stop()

    with st.spinner("Running data pipeline..."):

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_DIR / "src" / "run_pipeline.py")
            ],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        st.success("Pipeline completed successfully!")
        st.rerun()
    else:
        st.error("Pipeline execution failed.")
        with st.expander("View pipeline error"):
            st.code(result.stdout + "\n" + result.stderr)


# -------------------------------------------------
# 3. Load report data
# -------------------------------------------------

if not SALES_REPORT.exists():
    st.error("Sales report not found. Run the pipeline first.")
    st.stop()

try:
    with SALES_REPORT.open("r", encoding="utf-8") as file:
        sales_data = json.load(file)
except (OSError, json.JSONDecodeError) as error:
    st.error("Unable to read sales report: {}".format(error))
    st.stop()

metrics = sales_data["metrics"]

category_data = pd.DataFrame(
    sales_data["category_performance"]
)

daily_data = pd.DataFrame(
    sales_data["daily_sales"]
)


# -------------------------------------------------
# 4. Helper function
# -------------------------------------------------

def format_currency(value):
    return "₹{:,.2f}".format(value)


# -------------------------------------------------
# 5. Sales KPI cards
# -------------------------------------------------

st.header("Sales Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Orders",
        metrics["total_orders"]
    )

with col2:
    st.metric(
        "Delivered Orders",
        metrics["delivered_orders"]
    )

with col3:
    st.metric(
        "Cancelled Orders",
        metrics["cancelled_orders"]
    )

with col4:
    st.metric(
        "In-Progress Orders",
        metrics["in_progress_orders"]
    )

col5, col6 = st.columns(2)

with col5:
    st.metric(
        "Delivered Revenue",
        format_currency(metrics["delivered_revenue"])
    )

with col6:
    st.metric(
        "In-Progress Order Value",
        format_currency(metrics["in_progress_order_value"])
    )

st.info(
    "Delivered revenue includes only delivered orders. "
    "In-progress value is potential revenue, not realized revenue."
)


# -------------------------------------------------
# 6. Category performance chart
# -------------------------------------------------

st.header("Category Performance")

if not category_data.empty:

    category_data = category_data.sort_values(
        "delivered_revenue",
        ascending=False
    )

    st.bar_chart(
        category_data.set_index("category")[
            "delivered_revenue"
        ]
    )

    st.subheader("Category Details")

    st.dataframe(
        category_data,
        use_container_width=True
    )

else:
    st.warning("No category data available.")


# -------------------------------------------------
# 7. Daily sales trend
# -------------------------------------------------

st.header("Daily Delivered Revenue")

if not daily_data.empty:

    daily_data["order_date"] = pd.to_datetime(
        daily_data["order_date"]
    )

    daily_data = daily_data.sort_values("order_date")

    st.line_chart(
        daily_data.set_index("order_date")[
            "delivered_revenue"
        ]
    )

    with st.expander("View Daily Sales Data"):
        st.dataframe(
            daily_data,
            use_container_width=True
        )

else:
    st.warning("No daily sales data available.")


# -------------------------------------------------
# 8. Business performance indicators
# -------------------------------------------------

st.header("Business Performance")

total_orders = metrics["total_orders"]
delivered_orders = metrics["delivered_orders"]
cancelled_orders = metrics["cancelled_orders"]

if total_orders > 0:
    delivery_rate = delivered_orders / total_orders * 100
    cancellation_rate = cancelled_orders / total_orders * 100
else:
    delivery_rate = 0
    cancellation_rate = 0

col7, col8 = st.columns(2)

with col7:
    st.metric(
        "Delivery Rate",
        "{:.1f}%".format(delivery_rate)
    )

with col8:
    st.metric(
        "Cancellation Rate",
        "{:.1f}%".format(cancellation_rate)
    )


# -------------------------------------------------
# 9. AI-generated insights
# -------------------------------------------------

st.header("AI-Generated Business Insights")
st.caption("Generated locally using Ollama.")

if AI_REPORT.exists():

    insights = AI_REPORT.read_text(encoding="utf-8")

    if insights.strip():
        st.text(insights)
    else:
        st.warning("AI insights file is empty.")

else:
    st.warning("AI insights file not found.")


# -------------------------------------------------
# 10. Report metadata
# -------------------------------------------------

st.divider()

st.caption(
    "Report generated at: {}".format(
        sales_data["generated_at"]
    )
)

st.caption(
    "Source: {}".format(
        sales_data["source_table"]
    )
)

# -------------------------------------------------
# AI SALES CHATBOT
# -------------------------------------------------


# -------------------------------------------------
# AI SALES CHATBOT
# -------------------------------------------------

st.divider()

st.header("AI Sales Chatbot")

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Minimize Chat" if st.session_state.chat_open
        else "Open Chat"
    ):
        st.session_state.chat_open = (
            not st.session_state.chat_open
        )
        st.rerun()

with col2:
    if st.button("End Chat"):
        st.session_state.chat_messages = []
        st.session_state.chat_open = False
        st.rerun()

if st.session_state.chat_open:

    st.caption(
        "Ask questions about orders, revenue, "
        "categories and daily sales."
    )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a question about your sales data..."
    )

    if question:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing sales data..."):
                try:
                    answer = ask_sales_chatbot(question)
                except Exception as error:
                    answer = (
                        "Unable to generate an answer: {}".format(
                            error
                        )
                    )

            st.markdown(answer)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer
        })

else:
    st.info(
        "Chat is minimized. Click Open Chat to continue."
    )
