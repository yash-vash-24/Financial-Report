"""
Financial Report Generation System
Author: Yash Vashisth
Roll No: 2301730149

Description:
Core analysis module that loads financial data, computes key metrics and
ratios, detects trends, and produces structured insights that feed into
the AI-generated narrative report.
"""

import pandas as pd
import numpy as np
from datetime import datetime


def load_financial_data(path_or_df):
    """
    Load financial data from CSV path or accept a DataFrame directly.

    Expected columns: Date, Revenue, Expenses, Net_Income
    Optional columns: Assets, Liabilities, Cash_Flow
    """
    if isinstance(path_or_df, pd.DataFrame):
        df = path_or_df.copy()
    else:
        df = pd.read_csv(path_or_df)

    required = {"Date", "Revenue", "Expenses", "Net_Income"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    if df.empty:
        raise ValueError("No valid rows found after parsing Date values.")

    numeric_cols = [c for c in df.columns if c != "Date"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    required_numeric = ["Revenue", "Expenses", "Net_Income"]
    invalid_counts = df[required_numeric].isna().sum()
    bad_cols = [c for c in required_numeric if invalid_counts[c] > 0]
    if bad_cols:
        details = ", ".join(f"{c}({int(invalid_counts[c])})" for c in bad_cols)
        raise ValueError(
            "Invalid or missing numeric values in required columns: "
            f"{details}."
        )

    return df


def compute_metrics(df):
    """Compute aggregate financial metrics across the period."""
    metrics = {
        "period_start": df["Date"].min().strftime("%Y-%m-%d"),
        "period_end": df["Date"].max().strftime("%Y-%m-%d"),
        "total_revenue": float(df["Revenue"].sum()),
        "total_expenses": float(df["Expenses"].sum()),
        "total_net_income": float(df["Net_Income"].sum()),
        "avg_revenue": float(df["Revenue"].mean()),
        "avg_expenses": float(df["Expenses"].mean()),
        "avg_net_income": float(df["Net_Income"].mean()),
        "revenue_std": float(df["Revenue"].std() or 0),
        "periods": int(len(df))
    }

    if metrics["total_revenue"] > 0:
        metrics["profit_margin"] = round(
            metrics["total_net_income"] / metrics["total_revenue"] * 100, 2
        )
        metrics["expense_ratio"] = round(
            metrics["total_expenses"] / metrics["total_revenue"] * 100, 2
        )
    else:
        metrics["profit_margin"] = 0.0
        metrics["expense_ratio"] = 0.0

    if "Assets" in df.columns and "Liabilities" in df.columns:
        avg_assets = df["Assets"].mean()
        avg_liab = df["Liabilities"].mean()
        if avg_liab and avg_liab > 0:
            metrics["debt_to_asset"] = round(avg_liab / avg_assets, 2) if avg_assets else 0
        if avg_assets and avg_assets > 0:
            metrics["return_on_assets"] = round(
                metrics["total_net_income"] / avg_assets * 100, 2
            )

    if "Cash_Flow" in df.columns:
        metrics["total_cash_flow"] = float(df["Cash_Flow"].sum())
        metrics["avg_cash_flow"] = float(df["Cash_Flow"].mean())

    return metrics


def compute_growth(df):
    """Compute period-over-period growth rates."""
    growth = {}
    if len(df) < 2:
        return growth

    first_rev = df["Revenue"].iloc[0]
    last_rev = df["Revenue"].iloc[-1]
    if first_rev and first_rev != 0:
        growth["revenue_growth_pct"] = round((last_rev - first_rev) / abs(first_rev) * 100, 2)
    else:
        growth["revenue_growth_pct"] = 0.0

    first_ni = df["Net_Income"].iloc[0]
    last_ni = df["Net_Income"].iloc[-1]
    if first_ni and first_ni != 0:
        growth["net_income_growth_pct"] = round((last_ni - first_ni) / abs(first_ni) * 100, 2)
    else:
        growth["net_income_growth_pct"] = 0.0

    first_exp = df["Expenses"].iloc[0]
    last_exp = df["Expenses"].iloc[-1]
    if first_exp and first_exp != 0:
        growth["expense_growth_pct"] = round((last_exp - first_exp) / abs(first_exp) * 100, 2)
    else:
        growth["expense_growth_pct"] = 0.0

    return growth


def detect_trends(df):
    """Identify simple trends and anomalies using linear fits and z-scores."""
    trends = {}

    for col in ["Revenue", "Expenses", "Net_Income"]:
        if col not in df.columns or len(df) < 2:
            continue
        x = np.arange(len(df))
        y = df[col].values
        slope = np.polyfit(x, y, 1)[0]
        direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
        trends[col.lower() + "_trend"] = direction
        trends[col.lower() + "_slope"] = round(float(slope), 2)

    anomalies = []
    for col in ["Revenue", "Expenses", "Net_Income"]:
        if col not in df.columns:
            continue
        mean = df[col].mean()
        std = df[col].std()
        if std and std > 0:
            for _, row in df.iterrows():
                z = (row[col] - mean) / std
                if abs(z) > 2:
                    anomalies.append({
                        "date": row["Date"].strftime("%Y-%m-%d"),
                        "metric": col,
                        "value": float(row[col]),
                        "z_score": round(float(z), 2)
                    })

    trends["anomalies"] = anomalies
    return trends


def build_summary_package(df):
    """Bundle everything the AI narrative generator needs."""
    metrics = compute_metrics(df)
    growth = compute_growth(df)
    trends = detect_trends(df)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": metrics,
        "growth": growth,
        "trends": trends,
        "row_count": len(df)
    }


def sample_dataset():
    """Return a small deterministic sample dataset for demos and tests."""
    data = {
        "Date": pd.date_range("2023-01-01", periods=12, freq="MS"),
        "Revenue":   [120000, 135000, 128000, 142000, 155000, 160000,
                      158000, 172000, 180000, 175000, 190000, 205000],
        "Expenses":  [ 95000,  98000, 102000, 105000, 108000, 110000,
                      115000, 118000, 120000, 122000, 125000, 128000],
        "Net_Income":[ 25000,  37000,  26000,  37000,  47000,  50000,
                       43000,  54000,  60000,  53000,  65000,  77000],
        "Assets":    [500000, 510000, 515000, 525000, 540000, 550000,
                      560000, 575000, 590000, 595000, 610000, 630000],
        "Liabilities":[200000, 205000, 210000, 212000, 215000, 218000,
                       220000, 225000, 228000, 230000, 235000, 240000],
        "Cash_Flow": [ 20000,  22000,  19000,  25000,  30000,  32000,
                       28000,  35000,  40000,  36000,  45000,  52000]
    }
    return pd.DataFrame(data)


def main():
    """CLI demo."""
    print("\nFinancial Report Generation System - Demo Analysis")
    print("Author: Yash Vashisth (2301730149)\n")

    df = sample_dataset()
    package = build_summary_package(df)

    print(f"Period: {package['metrics']['period_start']} to {package['metrics']['period_end']}")
    print(f"Total Revenue   : {package['metrics']['total_revenue']:,.2f}")
    print(f"Total Net Income: {package['metrics']['total_net_income']:,.2f}")
    print(f"Profit Margin   : {package['metrics']['profit_margin']}%")
    print(f"Revenue Growth  : {package['growth'].get('revenue_growth_pct', 0)}%")
    print(f"Trend (revenue) : {package['trends'].get('revenue_trend', 'n/a')}")
    print(f"Anomalies found : {len(package['trends']['anomalies'])}")


if __name__ == "__main__":
    main()
