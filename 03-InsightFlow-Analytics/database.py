
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "retail_sample.csv"


def load_data():
    """Load and validate the prepared retail dataset."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "retail_sample.csv was not found. "
            "Run prepare_data.py first."
        )

    df = pd.read_csv(
        DATA_FILE,
        dtype={
            "InvoiceNo": str,
            "StockCode": str,
            "CustomerID": str,
        },
        keep_default_na=True,
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
    )

    df["Revenue"] = pd.to_numeric(
        df["Revenue"],
        errors="coerce",
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce",
    )

    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"],
        errors="coerce",
    )

    df["CustomerID"] = (
        df["CustomerID"]
        .fillna("")
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )

    df = df.dropna(
        subset=[
            "InvoiceDate",
            "Revenue",
            "Quantity",
            "UnitPrice",
        ]
    ).copy()

    return df


def create_connection(df):
    """Create an in-memory SQLite database."""
    connection = sqlite3.connect(":memory:")

    sql_df = df.copy()
    sql_df["InvoiceDate"] = (
        sql_df["InvoiceDate"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    sql_df.to_sql(
        "retail_transactions",
        connection,
        if_exists="replace",
        index=False,
    )

    connection.execute(
        """
        CREATE INDEX idx_invoice_date
        ON retail_transactions (InvoiceDate)
        """
    )

    connection.execute(
        """
        CREATE INDEX idx_country
        ON retail_transactions (Country)
        """
    )

    return connection


def run_query(connection, query, params=None):
    """Run a read-only SELECT query and return a DataFrame."""
    if not query.lstrip().upper().startswith("SELECT"):
        raise ValueError(
            "Only SELECT queries are supported."
        )

    return pd.read_sql_query(
        query,
        connection,
        params=params or (),
    )
