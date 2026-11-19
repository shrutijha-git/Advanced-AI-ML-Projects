
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (
    calculate_kpis,
    monthly_revenue,
    country_performance,
    top_products,
    customer_performance,
    generate_insights,
)
from database import (
    load_data,
    create_connection,
    run_query,
)


st.set_page_config(
    page_title="InsightFlow | Business Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------------------
# STYLING
# -------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .dashboard-subtitle {
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px;
        padding: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------
# LOAD DATA
# -------------------------------------------

@st.cache_data(show_spinner="Loading retail data...")
def get_data():
    return load_data()


try:
    df = get_data()

except Exception as error:
    st.error(
        "Unable to load the retail dataset. "
        "Make sure data/retail_sample.csv exists."
    )
    st.exception(error)
    st.stop()


if df.empty:
    st.warning("The dataset contains no transactions.")
    st.stop()


# -------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------

with st.sidebar:
    st.title("📊 InsightFlow")
    st.caption("E-Commerce Business Intelligence")

    st.divider()
    st.subheader("Filters")

    countries = sorted(
        df["Country"].dropna().unique().tolist()
    )

    selected_countries = st.multiselect(
        "Select countries",
        options=countries,
        default=[],
        placeholder="All countries",
    )

    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()

    selected_dates = st.date_input(
        "Transaction date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.divider()

    st.caption(
        "Source: UCI Online Retail dataset"
    )
    st.caption(
        "Figures are based on a cleaned sample "
        "of historical transactions."
    )
    st.caption(
        "Currency: British pounds (£)"
    )


# -------------------------------------------
# FILTER DATA
# -------------------------------------------

filtered = df.copy()

if selected_countries:
    filtered = filtered[
        filtered["Country"].isin(
            selected_countries
        )
    ]

if (
    isinstance(selected_dates, (tuple, list))
    and len(selected_dates) == 2
):
    start_date, end_date = selected_dates

    filtered = filtered[
        (filtered["InvoiceDate"].dt.date >= start_date)
        & (filtered["InvoiceDate"].dt.date <= end_date)
    ]


# -------------------------------------------
# DASHBOARD HEADER
# -------------------------------------------

st.markdown(
    '<div class="dashboard-title">'
    '📊 InsightFlow Analytics'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Interactive E-Commerce Sales & '
    'Business Intelligence Dashboard'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "This dashboard analyzes a cleaned sample of "
    "historical UK retail transactions. "
    "Revenue excludes canceled invoices, returns, "
    "and invalid sales rows."
)


# -------------------------------------------
# KPIs
# -------------------------------------------

kpis = calculate_kpis(filtered)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Revenue",
    f"£{kpis['revenue']:,.2f}",
)

col2.metric(
    "Orders",
    f"{kpis['orders']:,}",
)

col3.metric(
    "Customers",
    f"{kpis['customers']:,}",
)

col4.metric(
    "Avg. Order Value",
    f"£{kpis['average_order_value']:,.2f}",
)

col5.metric(
    "Units Sold",
    f"{kpis['units_sold']:,}",
)


if filtered.empty:
    st.warning(
        "No transactions match your filters. "
        "Please change the selected countries or dates."
    )
    st.stop()


# -------------------------------------------
# DASHBOARD TABS
# -------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Sales Overview",
        "🌍 Markets & Products",
        "👥 Customer Insights",
        "🗃️ SQL & Data Explorer",
    ]
)


# -------------------------------------------
# TAB 1 - SALES OVERVIEW
# -------------------------------------------

with tab1:
    st.subheader("Monthly Revenue Trend")

    monthly = monthly_revenue(filtered)

    fig_monthly = px.line(
        monthly,
        x="Month",
        y="Revenue",
        markers=True,
        title="Revenue by Month",
        labels={"Revenue": "Revenue (£)"},
    )

    fig_monthly.update_layout(
        hovermode="x unified",
        height=420,
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue by Country")

        countries_chart = country_performance(
            filtered, top_n=10
        )

        fig_countries = px.bar(
            countries_chart.sort_values("Revenue"),
            x="Revenue",
            y="Country",
            orientation="h",
            title="Top 10 Markets",
            labels={"Revenue": "Revenue (£)"},
        )

        st.plotly_chart(
            fig_countries,
            use_container_width=True,
        )

    with right:
        st.subheader("Order Volume by Month")

        order_df = filtered.copy()
        order_df["Month"] = (
            order_df["InvoiceDate"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_orders = (
            order_df.groupby("Month")["InvoiceNo"]
            .nunique()
            .reset_index(name="Orders")
        )

        fig_orders = px.bar(
            monthly_orders,
            x="Month",
            y="Orders",
            title="Unique Orders by Month",
        )

        st.plotly_chart(
            fig_orders,
            use_container_width=True,
        )

    st.subheader("💡 Business Observations")

    for insight in generate_insights(filtered):
        st.write(f"• {insight}")


# -------------------------------------------
# TAB 2 - MARKETS AND PRODUCTS
# -------------------------------------------

with tab2:
    st.subheader("Product Performance")

    product_df = top_products(
        filtered,
        top_n=15,
    )

    fig_products = px.bar(
        product_df.sort_values("Revenue"),
        x="Revenue",
        y="Description",
        orientation="h",
        title="Top 15 Products by Revenue",
        labels={"Revenue": "Revenue (£)"},
    )

    fig_products.update_layout(height=600)

    st.plotly_chart(
        fig_products,
        use_container_width=True,
    )

    st.subheader("Geographic Sales Distribution")

    geo_df = country_performance(
        filtered,
        top_n=100,
    )

    fig_geo = px.choropleth(
        geo_df,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        title="Revenue by Country",
        color_continuous_scale="Blues",
    )

    fig_geo.update_layout(height=480)

    st.plotly_chart(
        fig_geo,
        use_container_width=True,
    )

    st.caption(
        "Countries that cannot be matched by "
        "the map may not be displayed."
    )

    st.subheader("Top Products Table")

    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True,
    )


# -------------------------------------------
# TAB 3 - CUSTOMER INSIGHTS
# -------------------------------------------

with tab3:
    st.subheader("Customer Spending")

    customers_df = customer_performance(
        filtered
    )

    if customers_df.empty:
        st.info(
            "No customer IDs are available "
            "for the selected transactions."
        )

    else:
        top_customers = customers_df.head(15)

        fig_customers = px.bar(
            top_customers.sort_values("Revenue"),
            x="Revenue",
            y="CustomerID",
            orientation="h",
            title="Top 15 Customers by Revenue",
            labels={"Revenue": "Revenue (£)"},
        )

        fig_customers.update_layout(height=550)

        st.plotly_chart(
            fig_customers,
            use_container_width=True,
        )

        st.subheader("Customer Order Distribution")

        fig_distribution = px.histogram(
            customers_df,
            x="Orders",
            nbins=25,
            title="Orders per Identified Customer",
        )

        st.plotly_chart(
            fig_distribution,
            use_container_width=True,
        )

        st.caption(
            "Customer analysis includes only "
            "transactions with a known CustomerID."
        )


# -------------------------------------------
# TAB 4 - SQL AND DATA EXPLORER
# -------------------------------------------

with tab4:
    st.subheader("SQL Business Analytics")

    st.write(
        "Explore SQL-powered business metrics "
        "from the currently filtered transactions."
    )

    sql_queries = {
        "Revenue Summary": """
            SELECT
                ROUND(SUM(Revenue), 2) AS Revenue,
                COUNT(DISTINCT InvoiceNo) AS Orders,
                SUM(Quantity) AS UnitsSold
            FROM retail_transactions
        """,

        "Monthly Revenue": """
            SELECT
                SUBSTR(InvoiceDate, 1, 7) AS Month,
                ROUND(SUM(Revenue), 2) AS Revenue
            FROM retail_transactions
            GROUP BY SUBSTR(InvoiceDate, 1, 7)
            ORDER BY Month
        """,

        "Top 10 Countries": """
            SELECT
                Country,
                ROUND(SUM(Revenue), 2) AS Revenue,
                COUNT(DISTINCT InvoiceNo) AS Orders
            FROM retail_transactions
            GROUP BY Country
            ORDER BY Revenue DESC
            LIMIT 10
        """,

        "Top 10 Products": """
            SELECT
                Description,
                ROUND(SUM(Revenue), 2) AS Revenue,
                SUM(Quantity) AS UnitsSold
            FROM retail_transactions
            GROUP BY Description
            ORDER BY Revenue DESC
            LIMIT 10
        """,
    }

    selected_query = st.selectbox(
        "Choose a business query",
        options=list(sql_queries.keys()),
    )

    query = sql_queries[selected_query]

    st.code(query.strip(), language="sql")

    connection = create_connection(filtered)

    try:
        sql_result = run_query(
            connection,
            query,
        )
    finally:
        connection.close()

    st.dataframe(
        sql_result,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Transaction Data Explorer")

    st.dataframe(
        filtered.head(500),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="insightflow_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )


# -------------------------------------------
# FOOTER
# -------------------------------------------

st.divider()

st.caption(
    "InsightFlow Analytics | Advanced AI/ML Project 3 "
    "| Python • SQL • Pandas • Plotly • Streamlit"
)
