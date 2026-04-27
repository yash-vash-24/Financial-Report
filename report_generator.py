"""
Financial Report Generator - AI Narrative Module
Author: Yash Vashisth
Roll No: 2301730149

Description:
Uses a Hugging Face text generation model (GPT-2) to turn structured
financial metrics into a natural-language executive summary, with
deterministic template fallbacks for reliability.
"""

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*torchvision.*')

import os
import requests
from datetime import datetime

generator = None


def _get_local_generator():
    """Lazy-load a local text generation model for offline fallback."""
    global generator
    if generator is not None:
        return generator

    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "transformers is not installed. Install requirements or configure HF_API_TOKEN."
        ) from exc

    try:
        generator = pipeline("text-generation", model="distilgpt2", device=-1)
    except Exception:
        generator = pipeline("text-generation", model="gpt2", device=-1)
    return generator


def _api_polish(prompt, max_new_tokens=90):
    """Use Hugging Face Inference API when HF_API_TOKEN is configured."""
    token = os.getenv("HF_API_TOKEN", "").strip()
    if not token:
        return ""

    endpoint = os.getenv(
        "HF_API_URL",
        "https://api-inference.huggingface.co/models/distilgpt2"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False,
            "repetition_penalty": 1.2
        }
    }

    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=45)
        if resp.status_code >= 400:
            return ""
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"].strip()
            return text.split("\n\n")[0].strip()
    except Exception:
        return ""

    return ""


def _ai_polish(prompt, max_new_tokens=90):
    """Ask the model to extend a prompt into a short polished paragraph."""
    api_text = _api_polish(prompt, max_new_tokens=max_new_tokens)
    if api_text and len(api_text) > 20:
        return api_text

    try:
        local_generator = _get_local_generator()
        out = local_generator(
            prompt,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            truncation=True,
            pad_token_id=local_generator.tokenizer.eos_token_id,
            repetition_penalty=1.2
        )
        text = out[0]["generated_text"]
        if prompt in text:
            text = text.replace(prompt, "").strip()
        text = text.split("\n\n")[0]
        return text.strip()
    except Exception:
        return ""


def generate_executive_summary(package):
    """Produce the top-of-report narrative summary."""
    m = package["metrics"]
    g = package["growth"]

    base = (
        f"During the period from {m['period_start']} to {m['period_end']}, "
        f"the company recorded total revenue of {m['total_revenue']:,.0f} "
        f"and net income of {m['total_net_income']:,.0f}, "
        f"yielding a profit margin of {m['profit_margin']}%. "
        f"Revenue grew by {g.get('revenue_growth_pct', 0)}% "
        f"and net income by {g.get('net_income_growth_pct', 0)}% over the period."
    )

    prompt = f"Write a professional executive summary for a financial report. Facts: {base} Summary:"
    ai_text = _ai_polish(prompt, max_new_tokens=70)

    if ai_text and len(ai_text) > 40:
        return f"{base}\n\n{ai_text}"
    return base


def generate_insights(package):
    """Produce a list of bullet-style insights."""
    m = package["metrics"]
    g = package["growth"]
    t = package["trends"]
    insights = []

    margin = m["profit_margin"]
    if margin > 20:
        insights.append(f"Strong profitability: margin of {margin}% is above the 20% healthy threshold.")
    elif margin > 10:
        insights.append(f"Healthy profitability: margin of {margin}% is within the typical range.")
    elif margin > 0:
        insights.append(f"Thin margin of {margin}% suggests cost pressure; review expense lines.")
    else:
        insights.append(f"Negative margin of {margin}% — the business is loss-making for this period.")

    rev_growth = g.get("revenue_growth_pct", 0)
    if rev_growth > 15:
        insights.append(f"Revenue grew {rev_growth}% — well above double-digit growth expectations.")
    elif rev_growth > 5:
        insights.append(f"Revenue grew {rev_growth}% — solid, steady top-line expansion.")
    elif rev_growth > 0:
        insights.append(f"Revenue grew only {rev_growth}% — growth is modest; consider new revenue streams.")
    else:
        insights.append(f"Revenue declined by {abs(rev_growth)}% — investigate demand and pricing.")

    exp_growth = g.get("expense_growth_pct", 0)
    if exp_growth > rev_growth + 5:
        insights.append(
            f"Expenses are rising faster than revenue ({exp_growth}% vs {rev_growth}%). "
            "Cost discipline is needed."
        )
    elif exp_growth < rev_growth - 5:
        insights.append(
            f"Expenses are growing slower than revenue ({exp_growth}% vs {rev_growth}%). "
            "Operating leverage is improving."
        )

    rev_trend = t.get("revenue_trend")
    if rev_trend == "increasing":
        insights.append("Revenue trend is positive across the reporting period.")
    elif rev_trend == "decreasing":
        insights.append("Revenue trend is negative — warrants attention.")

    if "return_on_assets" in m:
        roa = m["return_on_assets"]
        if roa > 10:
            insights.append(f"Return on assets of {roa}% is strong.")
        elif roa > 0:
            insights.append(f"Return on assets of {roa}% is modest.")
        else:
            insights.append(f"Return on assets of {roa}% is negative — assets are not producing income.")

    if t.get("anomalies"):
        n = len(t["anomalies"])
        insights.append(
            f"{n} anomal{'y' if n == 1 else 'ies'} detected (>2 std dev). "
            "Review the flagged period(s) for one-off events."
        )

    return insights


def generate_recommendations(package):
    """Produce actionable recommendations based on the analysis."""
    m = package["metrics"]
    g = package["growth"]
    t = package["trends"]
    recs = []

    if m["profit_margin"] < 10:
        recs.append("Run a margin-improvement workstream: renegotiate top supplier contracts and review pricing.")

    if g.get("expense_growth_pct", 0) > g.get("revenue_growth_pct", 0):
        recs.append("Cap discretionary spend growth below revenue growth for the next two quarters.")

    if g.get("revenue_growth_pct", 0) < 5:
        recs.append("Commission a growth plan covering new segments, upsell, and geographic expansion.")

    if t.get("revenue_trend") == "decreasing":
        recs.append("Launch a demand-recovery initiative; diagnose churn, pricing, and competitive pressure.")

    if t.get("anomalies"):
        recs.append("Investigate the flagged anomaly periods and annotate one-off vs recurring events.")

    if "debt_to_asset" in m and m["debt_to_asset"] > 0.5:
        recs.append(f"Debt-to-asset ratio of {m['debt_to_asset']} is elevated; review refinancing options.")

    if "total_cash_flow" in m and m["total_cash_flow"] < 0:
        recs.append("Negative cumulative cash flow — tighten receivables and review working-capital cycle.")

    if not recs:
        recs.append("Maintain current operating discipline; revisit the framework in the next quarter.")

    return recs


def assemble_report(package, company_name="Company"):
    """Assemble the full text report."""
    m = package["metrics"]
    summary = generate_executive_summary(package)
    insights = generate_insights(package)
    recommendations = generate_recommendations(package)

    lines = []
    lines.append("=" * 70)
    lines.append(f"  FINANCIAL PERFORMANCE REPORT")
    lines.append(f"  {company_name}")
    lines.append(f"  Generated: {package['generated_at']}")
    lines.append("=" * 70)

    lines.append("\n## EXECUTIVE SUMMARY")
    lines.append(summary)

    lines.append("\n## KEY METRICS")
    lines.append(f"  Period            : {m['period_start']} to {m['period_end']}")
    lines.append(f"  Total Revenue     : {m['total_revenue']:,.2f}")
    lines.append(f"  Total Expenses    : {m['total_expenses']:,.2f}")
    lines.append(f"  Net Income        : {m['total_net_income']:,.2f}")
    lines.append(f"  Profit Margin     : {m['profit_margin']}%")
    lines.append(f"  Expense Ratio     : {m['expense_ratio']}%")
    if "return_on_assets" in m:
        lines.append(f"  Return on Assets  : {m['return_on_assets']}%")
    if "debt_to_asset" in m:
        lines.append(f"  Debt to Assets    : {m['debt_to_asset']}")
    if "total_cash_flow" in m:
        lines.append(f"  Total Cash Flow   : {m['total_cash_flow']:,.2f}")

    lines.append("\n## GROWTH")
    g = package["growth"]
    lines.append(f"  Revenue Growth    : {g.get('revenue_growth_pct', 0)}%")
    lines.append(f"  Net Income Growth : {g.get('net_income_growth_pct', 0)}%")
    lines.append(f"  Expense Growth    : {g.get('expense_growth_pct', 0)}%")

    lines.append("\n## INSIGHTS")
    for i, ins in enumerate(insights, 1):
        lines.append(f"  {i}. {ins}")

    lines.append("\n## RECOMMENDATIONS")
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    anomalies = package["trends"].get("anomalies", [])
    if anomalies:
        lines.append("\n## ANOMALIES DETECTED")
        for a in anomalies:
            lines.append(
                f"  - {a['date']}: {a['metric']} = {a['value']:,.2f} "
                f"(z-score {a['z_score']})"
            )

    lines.append("\n" + "=" * 70)
    lines.append("  Prepared by the Financial Report Generation System")
    lines.append("  Author: Yash Vashisth (2301730149)")
    lines.append("=" * 70)
    return "\n".join(lines)
