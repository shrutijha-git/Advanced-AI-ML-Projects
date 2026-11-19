
import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from analytics import (
    calculate_kpis,
    monthly_revenue,
    country_performance,
    top_products,
    customer_performance,
    generate_insights,
)

from database import (
    create_connection,
    run_query,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "InvoiceNo": ["1001", "1001", "1002", "1003"],
        "StockCode": ["A", "B", "A", "C"],
        "Description": [
            "Notebook", "Pen", "Notebook", "Bag"
        ],
        "Quantity": [2, 3, 1, 1],
        "UnitPrice": [10.0, 2.0, 10.0, 25.0],
        "Revenue": [20.0, 6.0, 10.0, 25.0],
        "CustomerID": ["101", "101", "102", ""],
        "Country": ["United Kingdom", "United Kingdom",
                    "France", "France"],
        "InvoiceDate": pd.to_datetime([
            "2021-01-05", "2021-01-05",
            "2021-02-06", "2021-02-07"
        ]),
    })


def test_kpis(sample_data):
    result = calculate_kpis(sample_data)

    assert result["revenue"] == pytest.approx(61.0)
    assert result["orders"] == 3
    assert result["customers"] == 2
    assert result["units_sold"] == 7
    assert result["average_order_value"] == pytest.approx(
        61.0 / 3
    )


def test_empty_kpis(sample_data):
    result = calculate_kpis(sample_data.iloc[0:0])
    assert result["revenue"] == 0
    assert result["orders"] == 0


def test_monthly_revenue(sample_data):
    result = monthly_revenue(sample_data)

    assert len(result) == 2
    assert result.iloc[0]["Revenue"] == pytest.approx(26.0)
    assert result.iloc[1]["Revenue"] == pytest.approx(35.0)


def test_country_performance(sample_data):
    result = country_performance(sample_data)

    france = result[
        result["Country"] == "France"
    ].iloc[0]

    assert france["Revenue"] == pytest.approx(35.0)
    assert france["Orders"] == 2


def test_top_products(sample_data):
    result = top_products(sample_data)

    assert result.iloc[0]["Description"] == "Notebook"
    assert result.iloc[0]["Revenue"] == pytest.approx(30.0)


def test_customer_performance(sample_data):
    result = customer_performance(sample_data)

    assert len(result) == 2
    assert result.iloc[0]["CustomerID"] == "101"
    assert result.iloc[0]["Revenue"] == pytest.approx(26.0)


def test_generate_insights(sample_data):
    result = generate_insights(sample_data)

    assert len(result) >= 2
    assert all(isinstance(item, str) for item in result)


def test_sql_query(sample_data):
    connection = create_connection(sample_data)

    try:
        result = run_query(
            connection,
            "SELECT SUM(Revenue) AS Total FROM retail_transactions"
        )

        assert result.iloc[0]["Total"] == pytest.approx(61.0)
    finally:
        connection.close()


def test_sql_rejects_non_select(sample_data):
    connection = create_connection(sample_data)

    try:
        with pytest.raises(ValueError):
            run_query(
                connection,
                "DELETE FROM retail_transactions"
            )
    finally:
        connection.close()
