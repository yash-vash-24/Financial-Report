# 📊 Financial Report Generation System

**AI-powered financial analysis** – Analyze financial data, detect trends, and generate comprehensive reports automatically.

## Features
- Automated computation of key financial metrics and ratios
- Period-over-period growth tracking
- Trend detection and anomaly flagging using z-scores
- AI-generated executive summary using Hugging Face Transformers
- Rule-based insights and actionable recommendations
- Interactive charts for revenue, expenses, cash flow, and assets
- Downloadable text reports and processed CSV

## Setup
```bash
python -m pip install -r requirements.txt
```

### Optional: Enable External AI API
This project supports two generation modes:
- API mode (preferred for assignment wording): Hugging Face Inference API
- Local fallback mode: local Transformers model (distilgpt2/gpt2)

To enable API mode, set:
```bash
export HF_API_TOKEN="your_huggingface_token"
# Optional custom endpoint:
# export HF_API_URL="https://api-inference.huggingface.co/models/distilgpt2"
```

## Run
```bash
# Web interface (recommended)
python -m streamlit run app.py

# CLI demo
python financial_analyzer.py
```

## Input Format
Upload a CSV with these columns:
- **Required:** Date, Revenue, Expenses, Net_Income
- **Optional:** Assets, Liabilities, Cash_Flow

A ready-to-use `sample_data.csv` ships with the project.

## Tech Stack
Python • Pandas • NumPy • Hugging Face Transformers • Streamlit

## Submission Artifacts
- Detailed implementation report: `IMPLEMENTATION_REPORT.md`
- Sample output document: `SAMPLE_OUTPUT.md`

### Issue: Generated narrative is incomplete
**Solution:** Increase `max_new_tokens` parameter in the `_ai_polish` function

### Issue: Columns not recognized
**Solution:** Match column names exactly — `Date`, `Revenue`, `Expenses`, `Net_Income`

### Issue: Model download takes too long on first run
**Solution:** First run downloads the GPT-2 model (~500MB) — subsequent runs load from cache

---

## References & Resources

- [Hugging Face Documentation](https://huggingface.co/)
- [Transformers Library](https://huggingface.co/docs/transformers)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## Author

**Name:** Gopesh Aggarwal
**Roll Number:** 2301730158
**Project:** Financial Report Generation System
**Date:** 2024-2025

---

## Conclusion

The Financial Report Generation System demonstrates practical application of Generative AI in automating financial analysis. By combining Pandas-based metric computation with Hugging Face narrative generation, we create an efficient tool that saves analyst time while keeping numerical accuracy deterministic.

This project showcases:
- Integration of modern AI APIs
- Practical data analysis automation
- User-friendly interface design
- Real-world application development

---

**Last Updated:** 2024
**Version:** 1.0
