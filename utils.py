from __future__ import annotations

import pandas as pd
from pandas.api.types import is_numeric_dtype

REQUIRED_COLUMNS = {
    "CustomerID",
    "Name",
    "Date",
    "CreditScore",
    "Income",
    "Debt",
}


def load_data(uploaded_file) -> pd.DataFrame:
    """
    Load and validate customer credit data.
    """

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")

    if df.empty:
        raise ValueError("The uploaded CSV is empty.")

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    # Parse dates safely
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert numeric columns safely
    for col in ["CreditScore", "Income", "Debt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows missing essential values
    df = df.dropna(
        subset=[
            "CustomerID",
            "Name",
            "CreditScore",
            "Income",
            "Debt",
        ]
    ).copy()

    # Prevent impossible negative values
    df["Income"] = df["Income"].clip(lower=0)
    df["Debt"] = df["Debt"].clip(lower=0)

    # Keep credit scores in a realistic range
    df["CreditScore"] = df["CreditScore"].clip(300, 850)

    return df.reset_index(drop=True)


def calculate_summary(df: pd.DataFrame) -> dict:
    """
    Calculate dashboard summary metrics.
    """

    if df.empty:
        return {
            "Total Customers": 0,
            "Average Credit Score": 0,
            "Average Income": 0,
            "Average Debt": 0,
        }

    return {
        "Total Customers": int(len(df)),
        "Average Credit Score": round(df["CreditScore"].mean(), 2),
        "Average Income": round(df["Income"].mean(), 2),
        "Average Debt": round(df["Debt"].mean(), 2),
    }


def credit_rating(score) -> str:
    """
    Convert credit score into rating.
    """

    try:
        score = float(score)
    except Exception:
        return "Unknown"

    if score >= 750:
        return "Excellent"

    if score >= 700:
        return "Good"

    if score >= 650:
        return "Fair"

    if score >= 600:
        return "Poor"

    return "Very Poor"


def debt_to_income_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Debt-to-Income ratio safely.
    """

    income = df["Income"].replace(0, pd.NA)

    ratio = (df["Debt"] / income) * 100

    return ratio.fillna(0).round(2)


def loan_eligibility(score, debt_to_income) -> str:
    """
    Rule-based loan eligibility.
    """

    try:
        score = float(score)
        debt_to_income = float(debt_to_income)
    except Exception:
        return "Not Eligible"

    if score >= 700 and debt_to_income <= 40:
        return "Eligible"

    return "Not Eligible"


def search_customers(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Search by customer ID or name.
    """

    if df.empty:
        return df

    if keyword is None:
        return df

    keyword = str(keyword).strip()

    if keyword == "":
        return df

    mask = (
        df["CustomerID"]
        .astype(str)
        .str.contains(keyword, case=False, na=False)
        |
        df["Name"]
        .astype(str)
        .str.contains(keyword, case=False, na=False)
    )

    return df.loc[mask].copy()
