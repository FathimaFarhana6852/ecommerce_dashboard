import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_ecommerce_sales.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df


df = load_data()

st.title("📊 Customer Analytics Dashboard")
st.caption(
    "Analyze customer behavior, sales trends, "
    "product performance and profitability."
)


st.sidebar.title("🔎Filters")

regions = sorted(df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)

segments = sorted(df["Customer_Segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

countries = sorted(df["Country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Country",
    countries,
    default=countries
)

categories = sorted(df["Product_Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Product Category",
    categories,
    default=categories
)

months = sorted(df["Order_YearMonth"].dropna().unique().tolist())
selected_months = st.sidebar.multiselect(
    "Order Month",
    months,
    default=months
)


filtered_df = df[
    df["Region"].isin(selected_regions)
    & df["Customer_Segment"].isin(selected_segments)
    & df["Country"].isin(selected_countries)
    & df["Product_Category"].isin(selected_categories)
    & df["Order_YearMonth"].isin(selected_months)
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


total_sales = filtered_df["Total_Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order_ID"].nunique()
total_customers = filtered_df["Customer_Name"].nunique()

average_order_value = (
    total_sales / total_orders if total_orders > 0 else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales", f"{total_sales:,.2f}")
col2.metric("Total Profit", f"{total_profit:,.2f}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Total Customers", f"{total_customers:,}")
col5.metric("Average Order Value", f"{average_order_value:,.2f}")

st.divider()


tab1, tab2, tab3 = st.tabs([
    "📈 Overview",
    "👥 Customer Analysis",
    "📦 Product Analysis"
])

with tab1:

    st.subheader("Sales Performance Overview")
    col1, col2 = st.columns(2)

    with col1:

        region_sales = (
            filtered_df.groupby("Region", as_index=False)["Total_Sales"]
            .sum()
            .sort_values("Total_Sales", ascending=False)
        )

        fig = px.bar(
            region_sales,
            x="Region",
            y="Total_Sales",
            title="Sales by Region",
            text_auto=".2s"
        )

        st.plotly_chart(fig, use_container_width=True)
    with col2:

        monthly_sales = (
            filtered_df.groupby("Order_YearMonth", as_index=False)["Total_Sales"]
            .sum()
            .sort_values("Order_YearMonth")
        )

        fig = px.line(
            monthly_sales,
            x="Order_YearMonth",
            y="Total_Sales",
            markers=True,
            title="Monthly Sales Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:

        segment_sales = (
            filtered_df.groupby("Customer_Segment", as_index=False)["Total_Sales"]
            .sum()
        )

        fig = px.pie(
            segment_sales,
            names="Customer_Segment",
            values="Total_Sales",
            title="Sales by Customer Segment",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)


    with col4:

        category_profit = (
            filtered_df.groupby("Product_Category", as_index=False)["Profit"]
            .sum()
            .sort_values("Profit", ascending=False)
        )

        fig = px.bar(
            category_profit,
            x="Product_Category",
            y="Profit",
            title="Profit by Product Category"
        )

        st.plotly_chart(fig, use_container_width=True)


    st.divider()
    st.subheader("💡 Sales Performance Insights")

    region_totals = filtered_df.groupby("Region")["Total_Sales"].sum()
    segment_totals = (
        filtered_df.groupby("Customer_Segment")["Total_Sales"].sum()
    )
    category_profits = (
        filtered_df.groupby("Product_Category")["Profit"].sum()
    )

    st.markdown(
        f"- **Regional Sales:** {region_totals.idxmax()} has the highest "
        f"sales ({region_totals.max():,.2f})."
    )

    st.markdown(
        f"- **Customer Segment:** {segment_totals.idxmax()} contributes "
        f"the highest sales ({segment_totals.max():,.2f})."
    )

    st.markdown(
        f"- **Profitability:** {category_profits.idxmax()} has the highest "
        f"total profit ({category_profits.max():,.2f})."
    )

    monthly_values = (
        filtered_df.groupby("Order_YearMonth")["Total_Sales"].sum().sort_index()
    )

    if len(monthly_values) >= 2:

        first_sales = monthly_values.iloc[0]
        last_sales = monthly_values.iloc[-1]

        if first_sales != 0:
            change_percent = (
                (last_sales - first_sales) / abs(first_sales)
            ) * 100

            st.markdown(
                f"- **Monthly Trend:** Sales changed by "
                f"{change_percent:.2f}% from {monthly_values.index[0]} "
                f"to {monthly_values.index[-1]}."
            )

        else:
            st.markdown(
                f"- **Monthly Trend:** Sales were "
                f"{last_sales:,.2f} in {monthly_values.index[-1]}, "
                f"compared with zero sales in the first selected month."
            )

with tab2:

    st.subheader("Customer Insights")

    customer_sales = (
        filtered_df.groupby("Customer_Name", as_index=False)
        .agg(
            Total_Sales=("Total_Sales", "sum"),
            Total_Orders=("Order_ID", "nunique"),
            Total_Profit=("Profit", "sum")
        )
        .sort_values("Total_Sales", ascending=False)
    )

    top_10_customers = customer_sales.head(10)

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            top_10_customers.sort_values("Total_Sales"),
            x="Total_Sales",
            y="Customer_Name",
            orientation="h",
            title="Top 10 Customers by Sales"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        segment_customers = (
            filtered_df.groupby("Customer_Segment", as_index=False)
            .agg(
                Customers=("Customer_Name", "nunique")
            )
        )

        fig = px.bar(
            segment_customers,
            x="Customer_Segment",
            y="Customers",
            title="Customers by Segment"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Sales Details")

    st.dataframe(
        customer_sales,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("💡 Customer Business Insights")

    customer_totals = (
        filtered_df.groupby("Customer_Name")["Total_Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    top_customer = customer_totals.idxmax()
    top_customer_sales = customer_totals.max()

    total_filtered_sales = filtered_df["Total_Sales"].sum()

    top_10_sales = customer_totals.head(10).sum()

    top_10_share = (
        top_10_sales / total_filtered_sales * 100
        if total_filtered_sales != 0 else 0
    )

    segment_counts = (
        filtered_df.groupby("Customer_Segment")["Customer_Name"]
        .nunique()
    )

    st.markdown(
        f"- **Top Customer:** {top_customer} has the highest sales "
        f"({top_customer_sales:,.2f})."
    )

    st.markdown(
        f"- **Top 10 Customers:** They contribute "
        f"{top_10_share:.2f}% of filtered sales."
    )

    st.markdown(
        f"- **Customer Segment:** {segment_counts.idxmax()} has the highest "
        f"number of unique customer names ({segment_counts.max()})."
    )

    st.markdown(
        "- **Recommended Action:** Consider loyalty offers for valuable "
        "customers and targeted campaigns to attract customers in other segments."
    )

    st.caption(
        "Customer counts are based on distinct customer names because "
        "the dataset does not contain a unique customer ID."
    )

with tab3:

    st.subheader("Product Performance")

    col1, col2 = st.columns(2)

    with col1:

        category_sales = (
            filtered_df.groupby("Product_Category", as_index=False)["Total_Sales"]
            .sum()
            .sort_values("Total_Sales", ascending=False)
        )

        fig = px.bar(
            category_sales,
            x="Product_Category",
            y="Total_Sales",
            title="Sales by Product Category"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        payment_sales = (
            filtered_df.groupby("Payment_Method", as_index=False)["Total_Sales"]
            .sum()
            .sort_values("Total_Sales", ascending=False)
        )

        fig = px.pie(
            payment_sales,
            names="Payment_Method",
            values="Total_Sales",
            title="Sales by Payment Method"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product Performance Details")

    product_performance = (
        filtered_df.groupby("Product_Name", as_index=False)
        .agg(
            Quantity_Sold=("Quantity", "sum"),
            Total_Sales=("Total_Sales", "sum"),
            Total_Profit=("Profit", "sum")
        )
        .sort_values("Total_Sales", ascending=False)
    )

    st.dataframe(
        product_performance,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("💡 Product Business Insights")

    category_sales_totals = (
        filtered_df.groupby("Product_Category")["Total_Sales"].sum()
    )

    category_profit_totals = (
        filtered_df.groupby("Product_Category")["Profit"].sum()
    )

    payment_totals = (
        filtered_df.groupby("Payment_Method")["Total_Sales"].sum()
    )

    product_sales_totals = (
        filtered_df.groupby("Product_Name")["Total_Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.markdown(
        f"- **Highest-Sales Category:** {category_sales_totals.idxmax()} "
        f"({category_sales_totals.max():,.2f})."
    )

    st.markdown(
        f"- **Most Profitable Category:** {category_profit_totals.idxmax()} "
        f"({category_profit_totals.max():,.2f} profit)."
    )

    st.markdown(
        f"- **Leading Payment Method:** {payment_totals.idxmax()} has the "
        f"highest sales ({payment_totals.max():,.2f})."
    )

    st.markdown(
        f"- **Top-Selling Product:** {product_sales_totals.idxmax()} has "
        f"the highest sales ({product_sales_totals.max():,.2f})."
    )

    st.markdown(
        "- **Recommended Action:** Review product sales and profit together "
        "before making inventory, pricing or discount decisions."
    )

st.divider()
st.subheader("📥 Export Data")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customer_analytics.csv",
    mime="text/csv"
)

st.caption(
    "Customer Analytics Dashboard | Built with Python, Pandas, Plotly and Streamlit"
)