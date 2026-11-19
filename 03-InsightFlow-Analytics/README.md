# 📊 InsightFlow Analytics — E-Commerce Business Intelligence Dashboard

**Advanced Project 3 | Python • SQL • Pandas • Plotly • Streamlit**

An interactive data analytics dashboard built using historical e-commerce transactions from the UCI Online Retail dataset.

InsightFlow Analytics helps explore sales performance, customer behavior, product trends, and geographic revenue distribution.

## Features

- Interactive revenue, customer, order, and unit-sales KPIs
- Country and transaction-date filters
- Monthly sales and order trends
- Top-performing products and countries
- Geographic revenue visualization
- Customer spending and order-frequency analysis
- SQL-powered business queries using SQLite
- Filtered transaction explorer
- Downloadable CSV reports
- Automated tests with Pytest
- Streamlit web interface

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Pandas | Data cleaning and analytics |
| SQLite | SQL queries |
| Plotly | Interactive visualization |
| Streamlit | Dashboard interface |
| Pytest | Automated testing |

## Dataset

**Source:** UCI Machine Learning Repository — Online Retail

https://archive.ics.uci.edu/dataset/352/online+retail

The source dataset contains historical transactions from a UK-based online retailer.

The preparation script removes canceled invoices, returns, invalid quantities, and invalid prices. It then generates a reproducible sample using complete invoices.

The deployed dashboard analyzes the cleaned sample, not the full original dataset.

**Currency:** GBP (£)

**Important:** Revenue represents recorded sales value, not profit. The dataset does not provide product costs.

## Project Structure

```text
03-InsightFlow-Analytics/
├── app.py
├── prepare_data.py
├── database.py
├── analytics.py
├── requirements.txt
├── README.md
├── data/
│   └── retail_sample.csv
├── sql/
│   └── business_queries.sql
├── tests/
│   └── test_analytics.py
└── screenshots/
```

## Local Installation

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\03-InsightFlow-Analytics\requirements.txt
```

## Prepare the Dataset

1. Download `Online Retail.xlsx` from the official UCI dataset page.
2. Place it in `03-InsightFlow-Analytics/data/`.
3. Run:

```powershell
python .\03-InsightFlow-Analytics\prepare_data.py
```

This generates `data/retail_sample.csv`.

## Launch the Dashboard

```powershell
python -m streamlit run .\03-InsightFlow-Analytics\app.py
```

Open `http://localhost:8501`.

## Run Automated Tests

```powershell
python -m pytest .\03-InsightFlow-Analytics\tests -v
```

## SQL Analytics

The `sql/business_queries.sql` file includes examples for:

- Total revenue
- Unique orders
- Average order value
- Monthly revenue
- Top countries
- Top products
- Top customers
- Daily sales performance

The interactive dashboard also runs predefined SQL queries against an in-memory SQLite database.

## Dashboard Sections

### 1. Sales Overview

Monthly revenue trends, order volume, market performance, and business observations.

### 2. Markets & Products

Top-selling products, revenue by country, and a geographic sales map.

### 3. Customer Insights

Customer spending, order frequency, and top customers with known IDs.

### 4. SQL & Data Explorer

SQL-powered summaries, transaction records, and CSV downloads.

## Screenshots

Screenshots will be added after the dashboard is tested.

## Live Demo

The public Streamlit deployment URL will be added after deployment.

## Limitations

- Uses a cleaned sample rather than the full original dataset.
- Historical data does not represent current market conditions.
- Canceled invoices and returns are excluded from revenue calculations.
- Customers without identifiers are excluded from unique-customer metrics.
- Product categories are not supplied by the original dataset.
- Revenue is not equivalent to profit.
- The dashboard is descriptive analytics, not a forecasting model.

## Future Improvements

- Revenue forecasting
- RFM customer segmentation
- Cohort and retention analysis
- Additional SQL analytics
- More comprehensive data quality reporting
- Full-dataset processing and incremental updates

## Status

Initial implementation — local testing and deployment pending.
