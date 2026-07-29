import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    calculate_summary,
    credit_rating,
    debt_to_income_ratio,
    loan_eligibility,
    search_customers,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="CreditSense AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Constants
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "CustomerID",
    "Name",
    "Date",
    "CreditScore",
    "Income",
    "Debt",
]

# --------------------------------------------------
# Custom Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .stMetric {
        border-radius:12px;
        padding:12px;
    }

    footer {
        visibility:hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("💳 CreditSense AI")

st.caption(
    "AI-powered Credit Score Analysis & Financial Health Dashboard"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Navigation")

st.sidebar.info(
    """
Upload a CSV file containing customer credit data.

Required columns:

• CustomerID
• Name
• Date
• CreditScore
• Income
• Debt
"""
)

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "data" not in st.session_state:
    st.session_state.data = None

# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
    accept_multiple_files=False,
)

# --------------------------------------------------
# Safe Data Loading
# --------------------------------------------------

if uploaded_file is not None:

    try:

        df = load_data(uploaded_file)

        st.session_state.data = df

    except Exception as e:

        st.error("Unable to load CSV.")

        st.exception(e)

        st.stop()

# --------------------------------------------------
# Wait Until File Uploaded
# --------------------------------------------------

if st.session_state.data is None:

    st.info("Upload a CSV file to begin analysis.")

    st.stop()

df = st.session_state.data.copy()
# --------------------------------------------------
# Dashboard Summary
# --------------------------------------------------

summary = calculate_summary(df)

st.markdown("## 📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Customers",
        summary["Total Customers"],
    )

with col2:
    st.metric(
        "Average Credit Score",
        summary["Average Credit Score"],
    )

with col3:
    st.metric(
        "Average Income",
        f"${summary['Average Income']:,.2f}",
    )

with col4:
    st.metric(
        "Average Debt",
        f"${summary['Average Debt']:,.2f}",
    )

st.divider()

# --------------------------------------------------
# Derived Columns
# --------------------------------------------------

try:

    df["Credit Rating"] = df["CreditScore"].apply(
        credit_rating
    )

    df["Debt-to-Income Ratio"] = debt_to_income_ratio(
        df
    )

    df["Loan Eligibility"] = df.apply(
        lambda row: loan_eligibility(
            row["CreditScore"],
            row["Debt-to-Income Ratio"],
        ),
        axis=1,
    )

except Exception as e:

    st.error(
        "Unable to calculate financial metrics."
    )

    st.exception(e)

    st.stop()

# --------------------------------------------------
# Quick Statistics
# --------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Credit Score")

    st.write(
        f"Minimum: {df['CreditScore'].min():.0f}"
    )

    st.write(
        f"Maximum: {df['CreditScore'].max():.0f}"
    )

    st.write(
        f"Median: {df['CreditScore'].median():.0f}"
    )

with right:

    st.subheader("Financial Health")

    eligible = (
        df["Loan Eligibility"]
        .eq("Eligible")
        .sum()
    )

    not_eligible = len(df) - eligible

    st.write(
        f"Eligible Customers: {eligible}"
    )

    st.write(
        f"Not Eligible: {not_eligible}"
    )

    st.write(
        f"Average DTI: "
        f"{df['Debt-to-Income Ratio'].mean():.2f}%"
    )

st.divider()
# --------------------------------------------------
# Customer Search
# --------------------------------------------------

st.markdown("## 🔍 Customer Records")

search_term = st.text_input(
    "Search by Customer ID or Name",
    placeholder="Enter Customer ID or customer name...",
)

try:

    filtered_df = search_customers(
        df,
        search_term,
    )

except Exception as e:

    st.error("Search failed.")

    st.exception(e)

    filtered_df = df.copy()

# --------------------------------------------------
# Handle Empty Results
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No matching customers found."
    )

else:

    st.success(
        f"Showing {len(filtered_df)} customer(s)."
    )

# --------------------------------------------------
# Display Customer Data
# --------------------------------------------------

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
)

# --------------------------------------------------
# CSV Download
# --------------------------------------------------

try:

    csv = filtered_df.to_csv(
        index=False,
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv,
        file_name="creditsense_filtered.csv",
        mime="text/csv",
    )

except Exception as e:

    st.error(
        "Unable to prepare CSV download."
    )

    st.exception(e)

st.divider()
# --------------------------------------------------
# Interactive Charts
# --------------------------------------------------

st.markdown("## 📈 Analytics Dashboard")

if filtered_df.empty:

    st.info("No data available for visualization.")

else:

    chart_col1, chart_col2 = st.columns(2)

    # ----------------------------------------------

    with chart_col1:

        st.subheader("Credit Rating Distribution")

        try:

            rating_counts = (
                filtered_df["Credit Rating"]
                .value_counts()
                .reset_index()
            )

            rating_counts.columns = [
                "Credit Rating",
                "Customers",
            ]

            fig = px.pie(
                rating_counts,
                names="Credit Rating",
                values="Customers",
                hole=0.45,
            )

            fig.update_layout(
                margin=dict(
                    l=20,
                    r=20,
                    t=40,
                    b=20,
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        except Exception as e:

            st.warning(
                "Unable to generate credit rating chart."
            )

    # ----------------------------------------------

    with chart_col2:

        st.subheader("Loan Eligibility")

        try:

            eligibility = (
                filtered_df["Loan Eligibility"]
                .value_counts()
                .reset_index()
            )

            eligibility.columns = [
                "Loan Eligibility",
                "Customers",
            ]

            fig = px.bar(
                eligibility,
                x="Loan Eligibility",
                y="Customers",
            )

            fig.update_layout(
                xaxis_title="",
                yaxis_title="Customers",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        except Exception:

            st.warning(
                "Unable to generate eligibility chart."
            )

# --------------------------------------------------
# Financial Charts
# --------------------------------------------------

if not filtered_df.empty:

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:

        st.subheader("Credit Score Distribution")

        try:

            fig = px.histogram(
                filtered_df,
                x="CreditScore",
                nbins=20,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        except Exception:

            st.warning(
                "Unable to generate credit score histogram."
            )

    with chart_col4:

        st.subheader("Income vs Debt")

        try:

            fig = px.scatter(
                filtered_df,
                x="Income",
                y="Debt",
                color="Credit Rating",
                hover_data=[
                    "CustomerID",
                    "Name",
                ],
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        except Exception:

            st.warning(
                "Unable to generate scatter plot."
            )

st.divider()
# --------------------------------------------------
# Customer Insights
# --------------------------------------------------

st.markdown("## 👤 Customer Insights")

if filtered_df.empty:

    st.info("No customer available.")

else:

    customer_options = (
        filtered_df["CustomerID"].astype(str)
        + " - "
        + filtered_df["Name"].astype(str)
    )

    selected = st.selectbox(
        "Select Customer",
        customer_options,
    )

    customer_id = selected.split(" - ")[0]

    customer = filtered_df[
        filtered_df["CustomerID"].astype(str)
        == customer_id
    ].iloc[0]

    left, right = st.columns(2)

    with left:

        st.subheader("Customer Information")

        st.write(f"**Customer ID:** {customer['CustomerID']}")
        st.write(f"**Name:** {customer['Name']}")
        st.write(f"**Credit Score:** {customer['CreditScore']:.0f}")
        st.write(f"**Credit Rating:** {customer['Credit Rating']}")
        st.write(f"**Income:** ₹{customer['Income']:,.2f}")
        st.write(f"**Debt:** ₹{customer['Debt']:,.2f}")

    with right:

        st.subheader("Financial Analysis")

        dti = customer["Debt-to-Income Ratio"]

        st.write(f"**Debt-to-Income Ratio:** {dti:.2f}%")

        eligibility = customer["Loan Eligibility"]

        if eligibility == "Eligible":
            st.success("✅ Eligible for Loan")
        else:
            st.error("❌ Not Eligible for Loan")

# --------------------------------------------------
# AI Recommendations
# --------------------------------------------------

    st.subheader("💡 Financial Recommendations")

    score = customer["CreditScore"]
    dti = customer["Debt-to-Income Ratio"]

    recommendations = []

    if score < 650:
        recommendations.append(
            "Improve payment history and avoid missed payments."
        )

    if dti > 40:
        recommendations.append(
            "Reduce existing debt before applying for new loans."
        )

    if customer["Income"] < customer["Debt"]:
        recommendations.append(
            "Increase income or reduce liabilities to improve financial health."
        )

    if score >= 750 and dti <= 30:
        recommendations.append(
            "Excellent financial profile. You may qualify for premium lending products."
        )

    if not recommendations:
        recommendations.append(
            "Financial profile appears healthy. Continue maintaining responsible credit usage."
        )

    for recommendation in recommendations:
        st.write(f"• {recommendation}")

st.divider()
# --------------------------------------------------
# Data Quality Report
# --------------------------------------------------

st.markdown("## 📋 Data Quality Report")

total_rows = len(df)

missing_values = int(df.isna().sum().sum())

duplicate_customers = int(
    df["CustomerID"].duplicated().sum()
)

invalid_scores = int(
    ((df["CreditScore"] < 300) |
     (df["CreditScore"] > 850)).sum()
)

negative_income = int(
    (df["Income"] < 0).sum()
)

negative_debt = int(
    (df["Debt"] < 0).sum()
)

quality_col1, quality_col2, quality_col3 = st.columns(3)

with quality_col1:

    st.metric(
        "Records",
        total_rows,
    )

    st.metric(
        "Missing Values",
        missing_values,
    )

with quality_col2:

    st.metric(
        "Duplicate Customers",
        duplicate_customers,
    )

    st.metric(
        "Invalid Credit Scores",
        invalid_scores,
    )

with quality_col3:

    st.metric(
        "Negative Income",
        negative_income,
    )

    st.metric(
        "Negative Debt",
        negative_debt,
    )

# --------------------------------------------------
# Dataset Health
# --------------------------------------------------

issues = []

if missing_values:
    issues.append(
        f"• {missing_values} missing value(s) detected."
    )

if duplicate_customers:
    issues.append(
        f"• {duplicate_customers} duplicate customer ID(s)."
    )

if invalid_scores:
    issues.append(
        f"• {invalid_scores} invalid credit score(s)."
    )

if negative_income:
    issues.append(
        f"• {negative_income} negative income value(s)."
    )

if negative_debt:
    issues.append(
        f"• {negative_debt} negative debt value(s)."
    )

st.subheader("Dataset Health")

if issues:

    st.warning(
        "Dataset contains potential data quality issues."
    )

    for issue in issues:
        st.write(issue)

else:

    st.success(
        "Dataset passed all quality checks."
    )

st.divider()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "CreditSense AI • Built with Streamlit, Pandas & Plotly"
    )
# --------------------------------------------------
# Application Summary
# --------------------------------------------------

st.markdown("---")

st.success("✅ CreditSense AI completed analysis successfully.")

with st.expander("Application Information"):

    st.write("Version: 1.0")

    st.write("Framework: Streamlit")

    st.write("Language: Python")

    st.write(f"Loaded Records: {len(df)}")

    st.write(
        f"Filtered Records: {len(filtered_df)}"
    )

# --------------------------------------------------
# Safe Cleanup
# --------------------------------------------------

try:

    del summary

except Exception:
    pass

try:

    del customer

except Exception:
    pass

# --------------------------------------------------
# End of Application
# --------------------------------------------------

st.caption(
    "© CreditSense AI | Educational Credit Analytics Dashboard"
)
