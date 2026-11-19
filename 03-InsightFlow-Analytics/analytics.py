
import pandas as pd


def calculate_kpis(df):
    """Calculate headline business metrics."""
    if df.empty:
        return {
            "revenue": 0.0,
            "orders": 0,
            "customers": 0,
            "average_order_value": 0.0,
            "units_sold": 0,
        }

    revenue = float(df["Revenue"].sum())
    orders = int(df["InvoiceNo"].nunique())

    valid_customers = (
        df["CustomerID"]
        .replace("", pd.NA)
        .dropna()
    )

    customers = int(valid_customers.nunique())

    return {
        "revenue": revenue,
        "orders": orders,
        "customers": customers,
        "average_order_value": (
            revenue / orders if orders else 0.0
        ),
        "units_sold": int(df["Quantity"].sum()),
    }


def monthly_revenue(df):
    """Aggregate revenue by calendar month."""
    if df.empty:
        return pd.DataFrame(
            columns=["Month", "Revenue"]
        )

    result = df.copy()

    result["Month"] = (
        result["InvoiceDate"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        result.groupby("Month", as_index=False)
        ["Revenue"]
        .sum()
        .sort_values("Month")
    )


def country_performance(df, top_n=10):
    """Revenue and order counts by country."""
    if df.empty:
        return pd.DataFrame(
            columns=["Country", "Revenue", "Orders"]
        )

    return (
        df.groupby("Country")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
        .head(top_n)
    )


def top_products(df, top_n=10):
    """Find the highest-revenue products."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Description",
                "Revenue",
                "Units",
            ]
        )

    return (
        df.groupby("Description")
        .agg(
            Revenue=("Revenue", "sum"),
            Units=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
        .head(top_n)
    )


def customer_performance(df):
    """Summarize customers with known customer IDs."""
    known = df[
        df["CustomerID"].notna()
        & (df["CustomerID"] != "")
    ].copy()

    if known.empty:
        return pd.DataFrame(
            columns=[
                "CustomerID",
                "Revenue",
                "Orders",
            ]
        )

    return (
        known.groupby("CustomerID")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )


def generate_insights(df):
    """Generate simple data-driven business observations."""
    if df.empty:
        return [
            "No transactions match the current filters."
        ]

    insights = []

    countries = country_performance(df, top_n=1)

    if not countries.empty:
        top_country = countries.iloc[0]
        total_revenue = df["Revenue"].sum()

        share = (
            top_country["Revenue"]
            / total_revenue * 100
            if total_revenue else 0
        )

        insights.append(
            f"{top_country['Country']} contributes "
            f"{share:.1f}% of filtered revenue."
        )

    products = top_products(df, top_n=1)

    if not products.empty:
        top_product = products.iloc[0]

        insights.append(
            f"The highest-revenue product is "
            f"{top_product['Description']}."
        )

    monthly = monthly_revenue(df)

    if not monthly.empty:
        best_month = monthly.loc[
            monthly["Revenue"].idxmax()
        ]

        insights.append(
            f"The highest-revenue month in the "
            f"selected data is {best_month['Month']}."
        )

    return insights
