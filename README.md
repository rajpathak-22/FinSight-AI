# FinSight AI — Intelligent Financial Intelligence & Decision Support System

An AI-powered financial analytics and decision-support dashboard built using Python, Streamlit, financial analysis, predictive analytics, anomaly detection, scenario modelling, and a locally hosted Large Language Model (LLM).

## Project Overview

FinSight AI transforms financial data into actionable business insights through automated financial analysis, interactive dashboards, forecasting, risk identification, scenario modelling, and AI-assisted executive reporting.

The project was developed to demonstrate the integration of Finance, Business Analytics, Python programming, and Generative AI in a practical business decision-making environment.

## Key Features

### 1. Financial Performance Dashboard
- Revenue and profitability analysis
- Gross Profit and Gross Margin
- Operating Profit and Operating Margin
- Expense analysis
- KPI monitoring
- Interactive data filtering

### 2. AI Financial Analyst
- Natural-language questions about financial data
- AI-generated financial interpretations
- Context-aware analysis based on dashboard data
- Locally hosted LLM using Ollama
- Python-calculated financial metrics used as the factual foundation

### 3. Financial Accuracy Audit
- Expense reconciliation
- Category-level expense verification
- Financial data validation
- Receivables analysis

### 4. Financial Anomaly Detection
Rule-based identification of unusual financial patterns, including:
- Significant month-over-month revenue declines
- Operating losses
- Unusual expense increases
- Gross margin deterioration

Anomaly flags indicate areas requiring investigation and do not independently establish the cause of an event.

### 5. Predictive Analytics & Forecasting
Implemented forecasting techniques:
- Moving Average
- Linear Trend
- Holt's Linear Trend

The system includes:
- Revenue forecasting
- Operating expense forecasting
- Operating profit forecasting
- Forecast comparison
- Backtesting
- MAE and RMSE evaluation
- Relative forecast error analysis

### 6. Financial Scenario Analysis
Interactive What-If Simulator allowing users to modify:
- Revenue growth or decline
- Gross margin assumptions
- Operating expense changes
- Salary expense changes

The simulator calculates the resulting revenue, gross profit, operating expenses, operating profit, and operating margin.

### 7. AI-Powered Executive Report Generator
Generates downloadable executive financial reports in PDF format, incorporating:
- Executive summary
- Financial KPI scorecard
- Revenue and profitability analysis
- Expense analysis
- Receivables and inventory insights
- Anomaly findings
- Forecasts and forecast accuracy
- Scenario analysis
- Management recommendations

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib
- OpenPyXL
- ReportLab
- Ollama
- Qwen 2.5 3B

## Project Architecture

Financial data is processed and analysed using Python. The resulting metrics and analytical outputs are presented through Streamlit dashboards.

Ollama provides locally hosted AI capabilities for interpreting calculated financial information and generating narrative insights.

**Core principle:** Financial calculations are performed programmatically, while AI is used primarily for interpretation and communication.

## Analytical Methodology

The project combines:

- Descriptive financial analytics
- Profitability analysis
- Expense analysis
- Receivables risk assessment
- Rule-based anomaly detection
- Time-series forecasting
- Forecast backtesting
- Scenario analysis
- AI-assisted financial interpretation

Forecast reliability is assessed using error metrics such as Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).

Scenario outputs are illustrative results based on user-defined assumptions and are not predictions of actual future performance.

## Dataset

The project uses a synthetic company dataset created for demonstration and analytical purposes.

The dataset includes:
- Sales transactions
- Products
- Customers
- Expenses
- Receivables
- Monthly financial summaries

No real company confidential information is included.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/FinSight-AI.git
cd FinSight-AI
```

### 2. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 3. Install Ollama

Download Ollama from:

https://ollama.com/

### 4. Download the AI model

```bash
ollama pull qwen2.5:3b
```

### 5. Run the application

```bash
py -m streamlit run app.py
```

Upload the required Excel dataset through the dashboard to begin analysis.

## Limitations

- The demonstration dataset is synthetic.
- Forecast models are based on a limited historical dataset.
- Backtesting observations are limited, and forecast reliability varies across financial metrics.
- Scenario analysis relies on simplified assumptions.
- Anomaly detection identifies unusual patterns but does not prove causation.
- AI-generated interpretations may require human review.
- Local AI functionality requires Ollama to be installed and running.

## Future Enhancements

- Cloud deployment
- Automated data ingestion
- Additional forecasting models
- Advanced financial risk analytics
- Automated report scheduling
- Industry benchmarking
- Improved scenario modelling
- Enhanced visualisation and reporting

## Author

**Raj Pathak**

PGDM — Finance & Business Analytics  
Jaipuria Institute of Management, Lucknow

---

*FinSight AI is an academic and portfolio project developed to demonstrate practical applications of financial analytics, business intelligence, predictive modelling, and artificial intelligence.*
