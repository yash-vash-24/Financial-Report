"""
Financial Report Generation System - Streamlit App
Author: Yash Vashisth
Roll No: 2301730149

Description:
Interactive web interface for uploading financial data, visualizing trends,
generating AI-assisted reports, and downloading the results.
"""

import streamlit as st
import pandas as pd
import io
from financial_analyzer import (
    load_financial_data,
    build_summary_package,
    sample_dataset
)
from report_generator import (
    assemble_report,
    generate_executive_summary,
    generate_insights,
    generate_recommendations
)

st.set_page_config(
    page_title="Financial Report Generator",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #0f4c75, #3282b8);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>📊 Financial Report Generation System</h1>
    <p>AI-assisted financial analysis and reporting</p>
    <p><b>Yash Vashisth</b> | Roll No: 2301730149</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📋 About")
    st.write(
        "Upload your financial data and let the system compute key metrics, "
        "detect trends, and generate a professional report with AI-powered "
        "narrative summary."
    )
    st.markdown("---")
    st.markdown("### 📄 Expected CSV Columns")
    st.write("**Required:** Date, Revenue, Expenses, Net_Income")
    st.write("**Optional:** Assets, Liabilities, Cash_Flow")
    st.markdown("---")
    st.markdown("### 🔧 Tech Stack")
    st.write("- Python\n- Pandas + NumPy\n- Hugging Face Transformers\n- Streamlit")


tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📈 Visualize", "📄 Generate Report"])

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.package = None

with tab1:
    st.subheader("Step 1 — Load Financial Data")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    with col_right:
        st.write("")
        st.write("")
        use_sample = st.button("📥 Use Sample Data", use_container_width=True)

    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            df = load_financial_data(raw)
            st.session_state.df = df
            st.session_state.package = build_summary_package(df)
            st.success(f"✅ Loaded {len(df)} rows.")
        except Exception as e:
            st.error(f"❌ Could not load file: {e}")

    if use_sample:
        df = sample_dataset()
        df = load_financial_data(df)
        st.session_state.df = df
        st.session_state.package = build_summary_package(df)
        st.success(f"✅ Sample data loaded ({len(df)} rows).")

    if st.session_state.df is not None:
        df = st.session_state.df
        pkg = st.session_state.package

        st.markdown("### Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("### Key Metrics")
        m = pkg["metrics"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"{m['total_revenue']:,.0f}")
        c2.metric("Net Income", f"{m['total_net_income']:,.0f}")
        c3.metric("Profit Margin", f"{m['profit_margin']}%")
        c4.metric("Expense Ratio", f"{m['expense_ratio']}%")

        g = pkg["growth"]
        c5, c6, c7 = st.columns(3)
        c5.metric("Revenue Growth", f"{g.get('revenue_growth_pct', 0)}%")
        c6.metric("Net Income Growth", f"{g.get('net_income_growth_pct', 0)}%")
        c7.metric("Expense Growth", f"{g.get('expense_growth_pct', 0)}%")

        anomalies = pkg["trends"].get("anomalies", [])
        if anomalies:
            st.warning(f"⚠️ {len(anomalies)} anomaly period(s) detected (>2 std dev).")
            st.dataframe(pd.DataFrame(anomalies), use_container_width=True)

with tab2:
    st.subheader("Trend Visualizations")
    if st.session_state.df is None:
        st.info("Load data in the first tab to see charts.")
    else:
        df = st.session_state.df
        chart_df = df.set_index("Date")

        st.markdown("#### Revenue, Expenses, Net Income")
        st.line_chart(chart_df[["Revenue", "Expenses", "Net_Income"]])

        if "Cash_Flow" in df.columns:
            st.markdown("#### Cash Flow")
            st.area_chart(chart_df[["Cash_Flow"]])

        if "Assets" in df.columns and "Liabilities" in df.columns:
            st.markdown("#### Assets vs Liabilities")
            st.bar_chart(chart_df[["Assets", "Liabilities"]])

with tab3:
    st.subheader("AI-Generated Financial Report")
    if st.session_state.df is None:
        st.info("Load data in the first tab to generate a report.")
    else:
        company = st.text_input("Company / Entity name:", value="Sample Corp")

        if st.button("🚀 Generate Report", use_container_width=True):
            with st.spinner("Generating narrative with AI... (first run downloads model)"):
                pkg = st.session_state.package
                report_text = assemble_report(pkg, company_name=company)

            st.markdown("### Executive Summary")
            st.info(generate_executive_summary(pkg))

            st.markdown("### Insights")
            for i, ins in enumerate(generate_insights(pkg), 1):
                st.write(f"{i}. {ins}")

            st.markdown("### Recommendations")
            for i, rec in enumerate(generate_recommendations(pkg), 1):
                st.write(f"{i}. {rec}")

            with st.expander("📄 View Full Text Report"):
                st.text(report_text)

            st.download_button(
                "⬇️ Download Report (.txt)",
                report_text,
                file_name=f"financial_report_{company.replace(' ', '_')}.txt",
                mime="text/plain"
            )

            buf = io.StringIO()
            st.session_state.df.to_csv(buf, index=False)
            st.download_button(
                "⬇️ Download Processed Data (.csv)",
                buf.getvalue(),
                file_name=f"processed_{company.replace(' ', '_')}.csv",
                mime="text/csv"
            )

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:12px;'>"
    "Financial Report Generation System | Yash Vashisth (2301730158) | "
    "Powered by Hugging Face & Transformers"
    "</div>",
    unsafe_allow_html=True
)
