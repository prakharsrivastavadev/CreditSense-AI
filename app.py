import streamlit as st
import plotly.express as px

from utils import (
    load_data,
    calculate_summary,
    credit_rating,
    loan_eligibility,
    debt_to_income_ratio,
    search_customers,
)

st.set_page_config(
    page_title="CreditSense AI",
    page_icon="💳",
    layout="wide",
)

st.title("💳 CreditSense AI")
st.caption("AI-Powered Credit Score Analysis & Loan Eligibility Dashboard")

uploaded_file = st.file_uploader(
    "Upload customer credit CSV",
    type=["csv"],
)

if uploaded_file:

    df = load_data(uploaded_file)

    st.subheader("Customer Data")
    st.dataframe(df, use_container_width=True)

    st.divider()

    summary = calculate_summary(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Customers",
        summary["Total Customers"],
    )

    col2.metric(
        "Avg Credit Score",
        f"{summary['Average Credit Score']:.0f}",
    )

    col3.metric(
        "Avg Income",
        f"₹{summary['Average Income']:,.2f}",
    )

    col4.metric(
        "Avg Debt",
        f"₹{summary['Average Debt']:,.2f}",
    )

    st.divider()

    st.subheader("Search Customers")

    keyword = st.text_input(
        "Search by Customer ID or Name"
    )

    filtered = search_customers(df, keyword).copy()

    filtered["Debt-to-Income (%)"] = debt_to_income_ratio(filtered)

    filtered["Credit Rating"] = filtered["CreditScore"].apply(
        credit_rating
    )

    filtered["Loan Eligibility"] = filtered.apply(
        lambda row: loan_eligibility(
            row["CreditScore"],
            row["Debt-to-Income (%)"],
        ),
        axis=1,
    )

    st.dataframe(filtered, use_container_width=True)

    st.divider()

    st.subheader("Credit Rating Distribution")

    rating_counts = (
        filtered["Credit Rating"]
        .value_counts()
        .reset_index()
    )

    rating_counts.columns = ["Rating", "Customers"]

    pie = px.pie(
        rating_counts,
        names="Rating",
        values="Customers",
        hole=0.4,
    )

    st.plotly_chart(
        pie,
        use_container_width=True,
    )

    st.subheader("Customer Credit Scores")

    bar = px.bar(
        filtered,
        x="Name",
        y="CreditScore",
        color="Credit Rating",
    )

    st.plotly_chart(
        bar,
        use_container_width=True,
    )

    st.subheader("Download Results")

    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False),
        file_name="credit_analysis.csv",
        mime="text/csv",
    )

else:
    st.info("Upload a customer credit CSV file to begin.")
