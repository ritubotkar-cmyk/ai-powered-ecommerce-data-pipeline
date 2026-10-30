# AI-Powered E-Commerce Data Engineering Pipeline

An end-to-end data engineering and generative AI portfolio project built using Python, PostgreSQL, SQL, Streamlit, Docker, and Ollama.

## Project Overview

This project demonstrates a complete e-commerce data pipeline that validates order data, loads records into PostgreSQL, generates SQL-based sales analytics, and produces AI-powered business insights.

It also includes an interactive Streamlit dashboard with a chatbot for asking natural-language questions about sales performance.

## Technology Stack

- Python 3.8
- PostgreSQL
- SQL and Pandas
- Streamlit
- Ollama (Qwen2.5 3B)
- Docker and Docker Compose
- Git and GitHub

## Architecture

CSV Data → Python Data Validation → PostgreSQL → SQL Analytics → JSON Reports → Streamlit Dashboard + Ollama AI Chatbot

## Key Features

- CSV ingestion and data-quality validation
- Duplicate detection and PostgreSQL upsert operations
- SQL analytics for delivered revenue and order status
- Category-wise and daily sales reporting
- AI-generated business insights
- Interactive AI sales chatbot
- Minimize and End Chat controls
- One-click pipeline execution from the dashboard
- Pipeline logging and automated validation tests
- Docker containerization

## Sample Dataset Results

| Metric | Value |
|---|---:|
| Total orders | 100 |
| Delivered orders | 30 |
| Cancelled orders | 23 |
| In-progress orders | 47 |
| Delivered revenue | ₹15,75,945 |
| In-progress order value | ₹17,88,280 |

These metrics come from generated demonstration data.

## Running Locally

1. Install Python, PostgreSQL and Ollama.
2. Create the `ecommerce_analytics` database and the required `raw_orders` table.
3. Install dependencies using `pip install -r requirements.txt`.
4. Create `.env` from `.env.example` and enter local database credentials.
5. Run `python src/run_pipeline.py`.
6. Launch the dashboard using `python -m streamlit run dashboard/app.py`.

## Running with Docker

1. Install Docker Desktop.
2. Configure `.env`.
3. Ensure PostgreSQL and Ollama are accessible from Docker.
4. Run `docker compose up --build -d`.
5. Open `http://localhost:8501`.

The Docker container runs the Python application and connects to PostgreSQL and Ollama hosted on the Windows computer.

## Automated Testing

Run:

`python -m unittest discover -s src -p "test_*.py" -v`

## Future Improvements

- Incremental data ingestion
- Advanced natural-language analytics
- Automated scheduling
- CI/CD using GitHub Actions
- Cloud deployment

## Project Purpose

This project demonstrates practical data engineering skills, including ETL development, data quality, PostgreSQL, SQL analytics, AI integration, dashboard development, and containerization.