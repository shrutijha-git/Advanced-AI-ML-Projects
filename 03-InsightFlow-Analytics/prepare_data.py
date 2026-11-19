
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

SOURCE_FILE = DATA_DIR / "Online Retail.xlsx"
OUTPUT_FILE = DATA_DIR / "retail_sample.csv"

SAMPLE_SIZE = 30000
RANDOM_SEED = 42


def prepare_data():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE_FILE}\n"
            "Download Online Retail.xlsx from UCI "
            "and place it inside the data folder."
        )

    print("Reading original retail dataset...")

    df = pd.read_excel(
        SOURCE_FILE,
        engine="openpyxl",
    )

    required_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(f"Original rows: {len(df):,}")

    df = df[required_columns].copy()

    df["InvoiceNo"] = (
        df["InvoiceNo"].astype(str).str.strip()
    )

    df["StockCode"] = (
        df["StockCode"].astype(str).str.strip()
    )

    df["Description"] = (
        df["Description"]
        .fillna("Unknown Product")
        .astype(str)
        .str.strip()
    )

    df["Country"] = (
        df["Country"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
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

    # Remove cancellations, returns, and invalid sales.
    valid = (
        ~df["InvoiceNo"].str.upper().str.startswith("C")
        & (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
        & df["InvoiceDate"].notna()
    )

    df = df.loc[valid].copy()

    df["CustomerID"] = df["CustomerID"].apply(
        lambda value: (
            str(int(value))
            if pd.notna(value)
            else ""
        )
    )

    df["Revenue"] = (
        df["Quantity"] * df["UnitPrice"]
    ).round(2)

    # Count invoice lines once, then sample complete orders.
    if len(df) > SAMPLE_SIZE:
        invoice_sizes = (
            df.groupby("InvoiceNo")
            .size()
            .sample(frac=1, random_state=RANDOM_SEED)
        )

        cumulative_rows = invoice_sizes.cumsum()

        selected_ids = invoice_sizes.index[
            (cumulative_rows - invoice_sizes) < SAMPLE_SIZE
        ]

        df = df[
            df["InvoiceNo"].isin(selected_ids)
        ].copy()

    df = df.sort_values(
        ["InvoiceDate", "InvoiceNo"]
    ).reset_index(drop=True)

    df["InvoiceDate"] = (
        df["InvoiceDate"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Cleaned sample rows: {len(df):,}")
    print(
        f"Unique orders: "
        f"{df['InvoiceNo'].nunique():,}"
    )
    print(
        f"Total sample revenue: "
        f"£{df['Revenue'].sum():,.2f}"
    )
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    prepare_data()
