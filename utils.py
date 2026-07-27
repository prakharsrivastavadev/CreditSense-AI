import pandas as pd


def load_data(uploaded_file):
    """Load customer credit data from a CSV file."""
    return pd.read_csv(uploaded_file, parse_dates=["Date"])


def calculate_summary(df):
    """Calculate overall credit metrics."""

    total_customers = len(df)
    average_credit_score = df["CreditScore"].mean()
    average_income = df["Income"].mean()
    average_debt = df["Debt"].mean()

    return {
        "Total Customers": total_customers,
        "Average Credit Score": average_credit_score,
        "Average Income": average_income,
        "Average Debt": average_debt,
    }


def credit_rating(score):
    """Return credit rating based on credit score."""

    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    elif score >= 600:
        return "Poor"
    else:
        return "Very Poor"


def loan_eligibility(score, debt_to_income):
    """Simple rule-based loan eligibility."""

    if score >= 700 and debt_to_income <= 40:
        return "Eligible"

    return "Not Eligible"


def debt_to_income_ratio(df):
    """Calculate debt-to-income ratio."""

    ratio = (df["Debt"] / df["Income"]) * 100

    return ratio.round(2)


def search_customers(df, keyword):
    """Search customers by name or ID."""

    if not keyword:
        return df

    keyword = keyword.lower()

    return df[
        df["CustomerID"].astype(str).str.lower().str.contains(keyword)
        | df["Name"].astype(str).str.lower().str.contains(keyword)
    ]
