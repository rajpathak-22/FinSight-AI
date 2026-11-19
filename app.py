
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="FinSight AI", page_icon="📊", layout="wide")

st.title("📊 FinSight AI")
st.caption("AI-powered financial intelligence and business decision support")

st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload your FinSight dataset (.xlsx)", type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload your FinSight_AI_Dataset.xlsx file to begin.")
    st.markdown("""
    **Expected workbook sheets:**
    - Sales
    - Products
    - Customers
    - Expenses
    - Receivables
    """)
    st.stop()

try:
    sales = pd.read_excel(uploaded_file, sheet_name="Sales")
    products = pd.read_excel(uploaded_file, sheet_name="Products")
    customers = pd.read_excel(uploaded_file, sheet_name="Customers")
    expenses = pd.read_excel(uploaded_file, sheet_name="Expenses")
    receivables = pd.read_excel(uploaded_file, sheet_name="Receivables")
except Exception as e:
    st.error(f"Could not read required workbook sheets: {e}")
    st.stop()

# Data preparation
sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
expenses["Date"] = pd.to_datetime(expenses["Date"], errors="coerce")
sales = sales.dropna(subset=["Date"])
expenses = expenses.dropna(subset=["Date"])
sales["Month"] = sales["Date"].dt.to_period("M").astype(str)
expenses["Month"] = expenses["Date"].dt.to_period("M").astype(str)

total_revenue = sales["Revenue"].sum()
total_cogs = sales["COGS"].sum()
gross_profit = sales["Gross_Profit"].sum()
total_expenses = expenses["Amount"].sum()
operating_profit = gross_profit - total_expenses
gross_margin = gross_profit / total_revenue * 100 if total_revenue else 0
operating_margin = operating_profit / total_revenue * 100 if total_revenue else 0
transaction_count = sales["Transaction_ID"].nunique()
avg_transaction = total_revenue / transaction_count if transaction_count else 0

# Sidebar filters
st.sidebar.subheader("Filters")
date_min = sales["Date"].min().date()
date_max = sales["Date"].max().date()
date_range = st.sidebar.date_input(
    "Transaction date range", value=(date_min, date_max),
    min_value=date_min, max_value=date_max
)
category_options = sorted(sales["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Product categories", category_options, default=category_options
)
region_options = sorted(sales["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Regions", region_options, default=region_options
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = pd.to_datetime(date_min), pd.to_datetime(date_max)

filtered_sales = sales[
    (sales["Date"] >= start_date) &
    (sales["Date"] <= end_date) &
    (sales["Category"].isin(selected_categories)) &
    (sales["Region"].isin(selected_regions))
].copy()

# For expenses, date filter is used, but category/region are not sales attributes.
filtered_expenses = expenses[
    (expenses["Date"] >= start_date) &
    (expenses["Date"] <= end_date)
].copy()

revenue = filtered_sales["Revenue"].sum()
cogs = filtered_sales["COGS"].sum()
gp = filtered_sales["Gross_Profit"].sum()
opex = filtered_expenses["Amount"].sum()
op_profit = gp - opex
gm = gp / revenue * 100 if revenue else 0
om = op_profit / revenue * 100 if revenue else 0
txn = filtered_sales["Transaction_ID"].nunique()
atv = revenue / txn if txn else 0

# Executive KPIs
st.subheader("Executive Overview")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue", f"₹{revenue:,.0f}")
k2.metric("Gross Profit", f"₹{gp:,.0f}")
k3.metric("Gross Margin", f"{gm:.1f}%")
k4.metric("Operating Profit", f"₹{op_profit:,.0f}")
k5.metric("Operating Margin", f"{om:.1f}%")

k6, k7, k8 = st.columns(3)
k6.metric("Transactions", f"{txn:,}")
k7.metric("Average Transaction Value", f"₹{atv:,.0f}")
k8.metric("Operating Expenses", f"₹{opex:,.0f}")

st.divider()

# Monthly trends
monthly = filtered_sales.groupby("Month").agg(
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit", "sum"),
    COGS=("COGS", "sum")
).reset_index()

monthly_opex = filtered_expenses.groupby("Month")["Amount"].sum().reset_index()
monthly_opex.columns = ["Month", "Operating_Expenses"]
monthly = monthly.merge(monthly_opex, on="Month", how="left")
monthly["Operating_Expenses"] = monthly["Operating_Expenses"].fillna(0)
monthly["Operating_Profit"] = monthly["Gross_Profit"] - monthly["Operating_Expenses"]

left, right = st.columns(2)
with left:
    st.subheader("Monthly Revenue")
    if not monthly.empty:
        fig = px.line(monthly, x="Month", y="Revenue", markers=True,
                      title="Revenue trend")
        fig.update_layout(yaxis_title="Revenue (₹)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Monthly Profitability")
    if not monthly.empty:
        fig = px.bar(monthly, x="Month", y=["Gross_Profit", "Operating_Profit"],
                     barmode="group", title="Gross vs Operating Profit")
        fig.update_layout(yaxis_title="Amount (₹)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

# Category analytics
st.subheader("Product Category Performance")
category = filtered_sales.groupby("Category").agg(
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit", "sum"),
    Units=("Quantity", "sum")
).reset_index()
category["Gross_Margin_%"] = np.where(
    category["Revenue"] != 0,
    category["Gross_Profit"] / category["Revenue"] * 100,
    0
)
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(category.sort_values("Revenue", ascending=False),
                 x="Category", y="Revenue", title="Revenue by Category")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.bar(category.sort_values("Gross_Margin_%", ascending=False),
                 x="Category", y="Gross_Margin_%", title="Gross Margin by Category")
    st.plotly_chart(fig, use_container_width=True)
st.dataframe(category.sort_values("Revenue", ascending=False), use_container_width=True)

# Expense analysis
st.subheader("Expense Intelligence")
expense_category = filtered_expenses.groupby("Expense_Category")["Amount"].sum().reset_index()
expense_category = expense_category.sort_values("Amount", ascending=False)
c1, c2 = st.columns(2)
with c1:
    fig = px.pie(expense_category, names="Expense_Category", values="Amount",
                 title="Operating Expense Mix")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.bar(expense_category, x="Expense_Category", y="Amount",
                 title="Expense by Category")
    st.plotly_chart(fig, use_container_width=True)

# Customers
st.subheader("Customer Analytics")
customer = filtered_sales.groupby("Customer_ID").agg(
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit", "sum"),
    Transactions=("Transaction_ID", "count")
).reset_index()
customer = customer.merge(
    customers[["Customer_ID", "Customer_Name", "Region", "Customer_Type"]],
    on="Customer_ID", how="left"
)
customer = customer.sort_values("Revenue", ascending=False)
st.dataframe(customer.head(15), use_container_width=True)

# Receivables
st.subheader("Receivables Risk")
ar = receivables.copy()
ar["Ageing_Bucket"] = pd.cut(
    ar["Days_Outstanding"],
    bins=[-1, 0, 30, 60, 90, 10000],
    labels=["Current", "1–30 days", "31–60 days", "61–90 days", "90+ days"]
)
ar_summary = ar.groupby("Ageing_Bucket", observed=False)["Outstanding_Balance"].sum().reset_index()
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(ar_summary, x="Ageing_Bucket", y="Outstanding_Balance",
                 title="Receivables Ageing")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    total_ar = ar["Outstanding_Balance"].sum()
    aged_60 = ar.loc[ar["Days_Outstanding"] > 60, "Outstanding_Balance"].sum()
    st.metric("Total Outstanding", f"₹{total_ar:,.0f}")
    st.metric("Outstanding > 60 days", f"₹{aged_60:,.0f}")
    st.metric("% of Receivables > 60 days", f"{aged_60/total_ar*100:.1f}%" if total_ar else "0%")

# Inventory alerts
st.subheader("Inventory Intelligence")
inventory = products.copy()
inventory["Stock_Status"] = np.where(
    inventory["Current_Stock"] <= inventory["Reorder_Level"],
    "REORDER REQUIRED", "Stock Available"
)
inventory["Inventory_Value"] = inventory["Current_Stock"] * inventory["Cost_Price"]
alerts = inventory[inventory["Stock_Status"] == "REORDER REQUIRED"]
if alerts.empty:
    st.success("No products currently meet the reorder alert threshold.")
else:
    st.warning(f"{len(alerts)} product(s) require reorder review.")
    st.dataframe(alerts, use_container_width=True)

st.subheader("All Inventory")
st.dataframe(inventory, use_container_width=True)

# Simple rule-based insights
st.subheader("Automated Business Insights")
insights = []
if not monthly.empty:
    worst = monthly.loc[monthly["Operating_Profit"].idxmin()]
    insights.append(
        f"Weakest month in the selected period: {worst['Month']} "
        f"(operating profit ₹{worst['Operating_Profit']:,.0f})."
    )
if not category.empty:
    top_rev = category.loc[category["Revenue"].idxmax()]
    top_margin = category.loc[category["Gross_Margin_%"].idxmax()]
    insights.append(
        f"Highest revenue category: {top_rev['Category']} "
        f"(₹{top_rev['Revenue']:,.0f})."
    )
    insights.append(
        f"Highest gross-margin category: {top_margin['Category']} "
        f"({top_margin['Gross_Margin_%']:.1f}%)."
    )
if not expense_category.empty:
    largest = expense_category.iloc[0]
    insights.append(
        f"Largest expense category: {largest['Expense_Category']} "
        f"(₹{largest['Amount']:,.0f})."
    )
if not alerts.empty:
    insights.append(
        f"Inventory alert: {len(alerts)} product(s) are at or below reorder level."
    )
for item in insights:
    st.write("• " + item)

st.caption("FinSight AI | Prototype analytics | Synthetic dataset — not real company data")


# ============================================================
# PHASE 5: FINANCIAL ANOMALY DETECTION (RULE-BASED, PYTHON)
# ============================================================
st.divider()
st.header("🔎 Financial Anomaly Detection")
st.caption("Python flags unusual monthly patterns using transparent thresholds. These are signals for review—not proof of a cause.")

if not monthly.empty:
    anomaly_data = monthly.sort_values("Month").copy()
    anomaly_data["Revenue_MoM_Change_%"] = anomaly_data["Revenue"].pct_change() * 100
    anomaly_data["Operating_Expense_MoM_Change_%"] = anomaly_data["Operating_Expenses"].pct_change() * 100
    anomaly_data["Gross_Margin_%"] = np.where(anomaly_data["Revenue"] != 0, anomaly_data["Gross_Profit"] / anomaly_data["Revenue"] * 100, 0)
    anomaly_data["Operating_Margin_%"] = np.where(anomaly_data["Revenue"] != 0, anomaly_data["Operating_Profit"] / anomaly_data["Revenue"] * 100, 0)

    anomaly_flags = []
    for _, row in anomaly_data.iterrows():
        flags = []
        if row["Operating_Profit"] < 0:
            flags.append("Operating loss")
        if pd.notna(row["Revenue_MoM_Change_%"]) and row["Revenue_MoM_Change_%"] <= -20:
            flags.append(f"Revenue dropped {abs(row['Revenue_MoM_Change_%']):.1f}% month-over-month")
        if pd.notna(row["Operating_Expense_MoM_Change_%"]) and row["Operating_Expense_MoM_Change_%"] >= 20:
            flags.append(f"Operating expenses increased {row['Operating_Expense_MoM_Change_%']:.1f}% month-over-month")
        if row["Gross_Margin_%"] < anomaly_data["Gross_Margin_%"].median() - 2:
            flags.append(f"Gross margin is {row['Gross_Margin_%']:.2f}%, more than 2 percentage points below period median")
        anomaly_flags.append("; ".join(flags))
    anomaly_data["Anomaly_Flags"] = anomaly_flags
    detected = anomaly_data[anomaly_data["Anomaly_Flags"] != ""].copy()

    if detected.empty:
        st.success("No monthly anomalies were detected using the current rules and selected filters.")
    else:
        st.warning(f"Detected {len(detected)} month(s) with one or more review flags.")
        show_cols = ["Month", "Revenue", "Gross_Profit", "Gross_Margin_%", "Operating_Expenses", "Operating_Profit", "Operating_Margin_%", "Revenue_MoM_Change_%", "Operating_Expense_MoM_Change_%", "Anomaly_Flags"]
        st.dataframe(detected[show_cols], use_container_width=True)
        for _, row in detected.iterrows():
            with st.expander(f"{row['Month']} — {row['Anomaly_Flags']}"):
                st.write(f"Revenue: ₹{row['Revenue']:,.0f} | Gross margin: {row['Gross_Margin_%']:.2f}% | Operating expenses: ₹{row['Operating_Expenses']:,.0f} | Operating profit: ₹{row['Operating_Profit']:,.0f}")
                st.caption("Flag indicates a statistical/rule-based signal for investigation. It does not establish the cause.")
else:
    st.info("Monthly data is unavailable for anomaly detection.")


# ============================================================
# PHASE 6: FINANCIAL FORECASTING & PREDICTIVE ANALYTICS
# ============================================================
st.divider()
st.header("📈 Financial Forecasting & Predictive Analytics")
st.caption("Forecasts are estimates based on selected historical data. With limited monthly observations, treat them as indicative—not decision-grade predictions.")

def moving_average_forecast(series, horizon=3, window=3):
    values = list(pd.Series(series, dtype=float).dropna())
    preds = []
    for _ in range(horizon):
        recent = values[-window:] if values else []
        pred = float(np.mean(recent)) if recent else 0.0
        preds.append(pred)
        values.append(pred)
    return preds

def linear_trend_forecast(series, horizon=3):
    values = np.asarray(pd.Series(series, dtype=float).dropna(), dtype=float)
    if len(values) < 2:
        return [float(values[-1]) if len(values) else 0.0] * horizon
    slope, intercept = np.polyfit(np.arange(len(values)), values, 1)
    return list((intercept + slope * np.arange(len(values), len(values)+horizon)).astype(float))

def holt_forecast(series, horizon=3, alpha=0.5, beta=0.3):
    values = np.asarray(pd.Series(series, dtype=float).dropna(), dtype=float)
    if len(values) == 0:
        return [0.0] * horizon
    if len(values) == 1:
        return [float(values[0])] * horizon
    level, trend = float(values[0]), float(values[1]-values[0])
    for value in values[1:]:
        old_level = level
        level = alpha*float(value) + (1-alpha)*(level+trend)
        trend = beta*(level-old_level) + (1-beta)*trend
    return [float(level+(i+1)*trend) for i in range(horizon)]

def forecast_model(series, model_name, horizon=1):
    if model_name == "3-Month Moving Average":
        return moving_average_forecast(series, horizon=horizon, window=3)
    if model_name == "Linear Trend":
        return linear_trend_forecast(series, horizon=horizon)
    return holt_forecast(series, horizon=horizon)

def backtest_models(series, test_size=3):
    values = pd.Series(series, dtype=float).dropna().reset_index(drop=True)
    names = ["3-Month Moving Average", "Linear Trend", "Holt's Linear Trend"]
    rows = []
    if len(values) <= test_size + 2:
        return pd.DataFrame(columns=["Model", "MAE", "RMSE", "Test Observations"])
    for name in names:
        actuals, predictions = [], []
        for idx in range(len(values)-test_size, len(values)):
            train = values.iloc[:idx]
            predictions.append(float(forecast_model(train, name, horizon=1)[0]))
            actuals.append(float(values.iloc[idx]))
        errors = np.asarray(actuals)-np.asarray(predictions)
        holdout_mean_abs = float(np.mean(np.abs(actuals))) if actuals else 0.0
        mae_value = float(np.mean(np.abs(errors)))
        rmse_value = float(np.sqrt(np.mean(errors**2)))
        rows.append({"Model": name, "MAE": mae_value,
                     "RMSE": rmse_value,
                     "MAE_%_of_Holdout_Mean": float(mae_value / holdout_mean_abs * 100) if holdout_mean_abs else None,
                     "RMSE_%_of_Holdout_Mean": float(rmse_value / holdout_mean_abs * 100) if holdout_mean_abs else None,
                     "Test Observations": len(actuals)})
    return pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)

if not monthly.empty and len(monthly) >= 6:
    fc_hist = monthly.sort_values("Month").copy()
    fc_hist["Month"] = pd.to_datetime(fc_hist["Month"]+"-01")
    fc_hist = fc_hist.set_index("Month").asfreq("MS")
    for metric in ["Revenue", "Operating_Expenses", "Operating_Profit"]:
        fc_hist[metric] = fc_hist[metric].fillna(0.0)

    forecast_horizon = st.selectbox("Forecast horizon", [3, 6], index=0, key="forecast_horizon")
    metric_labels = {"Revenue":"Revenue", "Operating_Expenses":"Operating Expenses", "Operating_Profit":"Operating Profit"}
    forecast_results, accuracy_tables, forecast_frames = {}, {}, []
    for metric, label in metric_labels.items():
        series = fc_hist[metric]
        accuracy = backtest_models(series, test_size=min(3, max(1, len(series)//4)))
        accuracy_tables[metric] = accuracy
        best_model = accuracy.iloc[0]["Model"] if not accuracy.empty else "Holt's Linear Trend"
        predictions = forecast_model(series, best_model, horizon=forecast_horizon)
        future_dates = pd.date_range(fc_hist.index.max()+pd.offsets.MonthBegin(1), periods=forecast_horizon, freq="MS")
        forecast_results[metric] = {
            "best_model": best_model,
            "mae": float(accuracy.iloc[0]["MAE"]) if not accuracy.empty else None,
            "rmse": float(accuracy.iloc[0]["RMSE"]) if not accuracy.empty else None,
            "mae_percent_of_holdout_mean": float(accuracy.iloc[0]["MAE_%_of_Holdout_Mean"]) if not accuracy.empty and pd.notna(accuracy.iloc[0]["MAE_%_of_Holdout_Mean"]) else None,
            "rmse_percent_of_holdout_mean": float(accuracy.iloc[0]["RMSE_%_of_Holdout_Mean"]) if not accuracy.empty and pd.notna(accuracy.iloc[0]["RMSE_%_of_Holdout_Mean"]) else None,
            "test_observations": int(accuracy.iloc[0]["Test Observations"]) if not accuracy.empty else 0,
            "forecast_dates": [d.strftime("%b %Y") for d in future_dates],
            "forecast_values": [float(v) for v in predictions]
        }
        forecast_frames.append(pd.DataFrame({"Month":future_dates,"Metric":label,"Forecast":predictions,"Model":best_model}))
    forecasts_long = pd.concat(forecast_frames, ignore_index=True)

    st.subheader("Model accuracy — holdout test")
    tabs = st.tabs(["Revenue","Operating Expenses","Operating Profit"])
    for tab, metric in zip(tabs, metric_labels.keys()):
        with tab:
            table = accuracy_tables[metric]
            if table.empty:
                st.info("Not enough history for model comparison.")
            else:
                display = table.copy()
                display["MAE"] = display["MAE"].map(lambda x:f"₹{x:,.0f}")
                display["RMSE"] = display["RMSE"].map(lambda x:f"₹{x:,.0f}")
                if "MAE_%_of_Holdout_Mean" in display.columns:
                    display["MAE (% of holdout mean)"] = display["MAE_%_of_Holdout_Mean"].map(lambda x:f"{x:.1f}%" if pd.notna(x) else "N/A")
                    display["RMSE (% of holdout mean)"] = display["RMSE_%_of_Holdout_Mean"].map(lambda x:f"{x:.1f}%" if pd.notna(x) else "N/A")
                    display = display.drop(columns=["MAE_%_of_Holdout_Mean","RMSE_%_of_Holdout_Mean"])
                st.dataframe(display, use_container_width=True, hide_index=True)
                st.caption("Lower MAE and RMSE indicate lower backtest error. Best model is selected by lowest RMSE.")

    st.subheader("Forecasts")
    for metric, label in metric_labels.items():
        historical = fc_hist[metric].reset_index()
        historical.columns = ["Month","Value"]
        future = forecasts_long[forecasts_long["Metric"]==label][["Month","Forecast"]].rename(columns={"Forecast":"Value"})
        chart_df = pd.concat([historical.assign(Series="Historical"),future.assign(Series="Forecast")],ignore_index=True)
        fig = px.line(chart_df,x="Month",y="Value",color="Series",markers=True,title=f"{label}: Historical vs Forecast")
        fig.update_layout(yaxis_title="INR (₹)",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        display_forecast=forecasts_long[forecasts_long["Metric"]==label].copy()
        display_forecast["Month"]=display_forecast["Month"].dt.strftime("%b %Y")
        display_forecast["Forecast"]=display_forecast["Forecast"].map(lambda x:f"₹{x:,.0f}")
        st.dataframe(display_forecast[["Month","Forecast","Model"]],use_container_width=True,hide_index=True)

    forecast_context = {
        "methodology":"Expanding-window one-step-ahead backtest on the last up to 3 months; models compared using MAE and RMSE. Future forecast uses the lowest-RMSE model for each metric. Relative errors are shown as a percentage of the mean absolute holdout actual value.",
        "caveat":"Only up to 3 holdout observations are used, so model ranking is uncertain. Expanding-window testing helps avoid future-data leakage; it does not inherently cause overfitting. Short monthly history; forecasts are indicative and may be unreliable. Seasonality is not modeled.",
        "forecast_horizon_months":forecast_horizon,
        "metrics":forecast_results
    }
else:
    forecast_context={"status":"Insufficient monthly data; at least 6 months are required."}
    st.info("Forecasting requires at least six monthly observations after filters. Adjust filters to include more history.")


# ============================================================
# PHASE 7: FINANCIAL SCENARIO ANALYSIS & WHAT-IF SIMULATOR
# ============================================================
st.divider()
st.header("🧪 Financial Scenario Analysis & What-If Simulator")
st.caption("Change assumptions to simulate potential outcomes. Scenarios are illustrative—not predictions or actual results.")

scenario_revenue_change = st.slider("Revenue change (%)", -30, 30, 0, 1, key="scenario_revenue_change")
scenario_margin_change_pp = st.slider("Gross margin change (percentage points)", -5.0, 5.0, 0.0, 0.5, key="scenario_margin_change")
scenario_opex_change = st.slider("Operating expense change (%)", -30, 30, 0, 1, key="scenario_opex_change")
scenario_salary_change = st.slider("Salary expense change (%)", -20, 30, 0, 1, key="scenario_salary_change")

base_revenue = float(revenue)
base_gross_profit = float(gp)
base_gross_margin = float(gm) / 100.0 if abs(float(gm)) > 1 else float(gm)
base_opex = float(opex)
base_operating_profit = float(op_profit)

salary_base = float(expense_category.loc[expense_category["Expense_Category"].astype(str).str.contains(r"salari|salary", case=False, na=False, regex=True), "Amount"].sum()) if not expense_category.empty else 0.0
other_opex_base = max(0.0, base_opex - salary_base)

scenario_revenue = base_revenue * (1 + scenario_revenue_change / 100.0)
scenario_gross_margin = min(1.0, max(-1.0, base_gross_margin + scenario_margin_change_pp / 100.0))
scenario_gross_profit = scenario_revenue * scenario_gross_margin
scenario_salary = salary_base * (1 + scenario_salary_change / 100.0)
scenario_other_opex = other_opex_base * (1 + scenario_opex_change / 100.0)
scenario_opex = scenario_salary + scenario_other_opex
scenario_operating_profit = scenario_gross_profit - scenario_opex
scenario_operating_margin = scenario_operating_profit / scenario_revenue * 100 if scenario_revenue else 0.0

scenario_base = pd.DataFrame([
    {"Metric":"Revenue","Baseline":base_revenue,"Scenario":scenario_revenue},
    {"Metric":"Gross Profit","Baseline":base_gross_profit,"Scenario":scenario_gross_profit},
    {"Metric":"Operating Expenses","Baseline":base_opex,"Scenario":scenario_opex},
    {"Metric":"Operating Profit","Baseline":base_operating_profit,"Scenario":scenario_operating_profit},
])
scenario_base["Change"] = scenario_base["Scenario"] - scenario_base["Baseline"]
scenario_base["Change_%"] = np.where(scenario_base["Baseline"] != 0, scenario_base["Change"] / scenario_base["Baseline"] * 100, np.nan)

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Scenario Revenue", f"₹{scenario_revenue:,.0f}", f"{scenario_revenue_change:+.1f}%")
sc2.metric("Scenario Operating Profit", f"₹{scenario_operating_profit:,.0f}", f"₹{scenario_operating_profit-base_operating_profit:,.0f}")
sc3.metric("Scenario Operating Margin", f"{scenario_operating_margin:.2f}%", f"{scenario_operating_margin-float(om):+.2f} pp")

st.subheader("Baseline vs Scenario")
scenario_display = scenario_base.copy()
for col in ["Baseline","Scenario","Change"]:
    scenario_display[col] = scenario_display[col].map(lambda x: f"₹{x:,.0f}")
scenario_display["Change_%"] = scenario_display["Change_%"].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
st.dataframe(scenario_display, use_container_width=True, hide_index=True)

chart_data = scenario_base.melt(id_vars="Metric", value_vars=["Baseline","Scenario"], var_name="Case", value_name="Amount")
fig = px.bar(chart_data, x="Metric", y="Amount", color="Case", barmode="group", title="Baseline vs Scenario Financial Impact")
fig.update_layout(yaxis_title="INR (₹)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Break-even / Target Operating Margin Calculator")
target_margin = st.slider("Target operating margin (%)", 0.0, 30.0, 10.0, 0.5, key="target_margin")
target_margin_decimal = target_margin / 100.0
denominator = scenario_gross_margin - target_margin_decimal
required_revenue = scenario_opex / denominator if denominator > 0 else None
if required_revenue is not None and required_revenue >= 0:
    st.metric(f"Revenue required for {target_margin:.1f}% operating margin", f"₹{required_revenue:,.0f}")
    st.caption("Calculation assumes the selected scenario gross margin remains constant and operating expenses remain fixed at the scenario level.")
else:
    st.warning("The selected gross margin is not greater than the target operating margin. Under these assumptions, no finite revenue target can achieve the requested operating margin.")

scenario_context = {
    "description":"Interactive illustrative what-if scenario, not a forecast",
    "assumptions":{
        "revenue_change_percent":scenario_revenue_change,
        "gross_margin_change_percentage_points":scenario_margin_change_pp,
        "operating_expense_change_percent_for_non_salary_expenses":scenario_opex_change,
        "salary_expense_change_percent":scenario_salary_change,
        "salary_baseline_inr":round(salary_base,2),
        "non_salary_operating_expenses_baseline_inr":round(other_opex_base,2)
    },
    "baseline":{
        "revenue_inr":round(base_revenue,2),
        "gross_profit_inr":round(base_gross_profit,2),
        "gross_margin_percent":round(base_gross_margin*100,4),
        "operating_expenses_inr":round(base_opex,2),
        "operating_profit_inr":round(base_operating_profit,2),
        "operating_margin_percent":round(float(om),4)
    },
    "scenario":{
        "revenue_inr":round(scenario_revenue,2),
        "gross_profit_inr":round(scenario_gross_profit,2),
        "gross_margin_percent":round(scenario_gross_margin*100,4),
        "operating_expenses_inr":round(scenario_opex,2),
        "operating_profit_inr":round(scenario_operating_profit,2),
        "operating_margin_percent":round(scenario_operating_margin,4)
    },
    "target_operating_margin_percent":target_margin,
    "required_revenue_for_target_margin_inr":round(required_revenue,2) if required_revenue is not None and required_revenue >= 0 else None,
    "target_revenue_assumption":"Gross margin held constant at scenario value; scenario operating expenses held fixed."
}

# ============================================================
# PHASE 4: LOCAL AI FINANCIAL ANALYST (OLLAMA)
# ============================================================
st.divider()

# Phase 8 — Business Decision Intelligence
st.divider()
st.header("🧭 Business Decision Intelligence & Management Action Plan")
st.caption("Rule-based recommendations are generated from calculated dashboard metrics. Thresholds are screening heuristics—not industry benchmarks or guarantees.")

# Transparent financial health score (100 points)
score_profit = 25 if op_profit > 0 else 0
score_margin = 20 if om >= 10 else (15 if om >= 5 else (8 if om >= 0 else 0))
score_receivables = 20 if (total_ar and aged_60 / total_ar <= 0.10) else (12 if (total_ar and aged_60 / total_ar <= 0.25) else 5)
score_inventory = 15 if alerts.empty else max(0, 15 - 5 * len(alerts))
score_revenue_stability = 20
if len(monthly) >= 2:
    rev_changes = monthly["Revenue"].pct_change().dropna()
    large_declines = int((rev_changes <= -0.20).sum())
    score_revenue_stability = max(0, 20 - 5 * large_declines)
health_score = int(score_profit + score_margin + score_receivables + score_inventory + score_revenue_stability)
health_label = "Strong" if health_score >= 80 else ("Moderate" if health_score >= 60 else "Needs Attention")

h1, h2, h3 = st.columns(3)
h1.metric("Financial Health Score", f"{health_score}/100")
h2.metric("Overall Assessment", health_label)
h3.metric("Priority Issues Detected", "—")

score_details = pd.DataFrame([
    {"Dimension":"Operating profitability","Score":score_profit,"Maximum":25,"Basis":"Positive operating profit"},
    {"Dimension":"Operating margin","Score":score_margin,"Maximum":20,"Basis":"Margin screening bands: 10%, 5%, and 0%"},
    {"Dimension":"Receivables ageing","Score":score_receivables,"Maximum":20,"Basis":"Share of receivables outstanding >60 days"},
    {"Dimension":"Inventory reorder exposure","Score":score_inventory,"Maximum":15,"Basis":"Deduction for products at/below reorder level"},
    {"Dimension":"Revenue stability","Score":score_revenue_stability,"Maximum":20,"Basis":"Deduction for monthly revenue drops ≥20%"},
])
with st.expander("How the health score is calculated"):
    st.dataframe(score_details,hide_index=True,use_container_width=True)
    st.info("This is a prototype screening score with arbitrary transparent weights. It is not a credit rating, investment rating, or industry-benchmarked assessment.")

recommendations = []
def add_rec(priority, area, finding, action, kpi, timeframe):
    recommendations.append({"Priority":priority,"Area":area,"Evidence / Finding":finding,
                            "Recommended Management Action":action,"Suggested KPI":kpi,"Timeframe":timeframe})

if op_profit <= 0:
    add_rec("Critical","Profitability",f"Operating profit is ₹{op_profit:,.0f}.",
            "Review pricing, product contribution, discretionary spending and fixed-cost capacity; prepare a recovery plan.",
            "Operating profit; operating margin","Immediate (1–2 weeks)")
elif om < 5:
    add_rec("High","Profitability",f"Operating margin is {om:.2f}%, below the 5% screening threshold.",
            "Conduct a margin bridge by category and expense line; prioritize controllable costs and low-contribution products.",
            "Operating margin; contribution by category","Within 30 days")
elif om < 10:
    add_rec("Medium","Profitability",f"Operating margin is {om:.2f}%.",
            "Monitor gross-margin mix and operating-cost growth; identify incremental margin improvement opportunities.",
            "Operating margin; expense-to-revenue ratio","Within 30 days")

if not monthly.empty and len(monthly) >= 2:
    monthly_sorted = monthly.sort_values("Month")
    monthly_sorted["Revenue_MoM_%"] = monthly_sorted["Revenue"].pct_change() * 100
    drop_months = monthly_sorted[monthly_sorted["Revenue_MoM_%"] <= -20]
    if not drop_months.empty:
        drop_list = ", ".join(f"{r['Month']} ({r['Revenue_MoM_%']:.1f}%)" for _,r in drop_months.iterrows())
        add_rec("High","Revenue volatility",f"Monthly revenue declined by ≥20% in: {drop_list}.",
                "Validate the sales pipeline, customer/order timing, category and region mix; investigate whether the decline is temporary or structural.",
                "Monthly revenue; order volume; customer retention","Within 2 weeks")

if total_ar > 0:
    aged60_pct = aged_60 / total_ar * 100
    if aged60_pct > 25:
        pr = "High"
    elif aged60_pct > 10:
        pr = "Medium"
    else:
        pr = "Low"
    if aged60_pct > 10:
        add_rec(pr,"Receivables",f"₹{aged_60:,.0f} ({aged60_pct:.1f}%) of receivables are >60 days overdue.",
                "Create an ageing-based collection list, assign account owners, contact overdue customers and review credit terms for repeat delays.",
                "Overdue >60 days; collection rate; DSO","Weekly until improved")

if not alerts.empty:
    names = ", ".join(alerts["Product_Name"].astype(str).tolist())
    add_rec("Medium","Inventory",f"{len(alerts)} product(s) are at/below reorder level: {names}.",
            "Confirm demand and supplier lead time before replenishing; prioritize products with high sales velocity and avoid blind over-ordering.",
            "Stockout rate; inventory turnover; reorder fulfilment","Within 1 week")

if not category.empty:
    low_margin = category[category["Gross_Margin_%"] < category["Gross_Margin_%"].median()]
    if not low_margin.empty:
        low_names = ", ".join(low_margin.sort_values("Revenue",ascending=False)["Category"].head(3).astype(str))
        add_rec("Medium","Product mix",f"Categories below the dataset's median gross margin include: {low_names}.",
                "Review discounting, purchase costs and product mix in these categories; assess whether targeted price or sourcing changes are feasible.",
                "Gross margin by category; discount rate","Within 30 days")

if not expense_category.empty and revenue > 0:
    largest_expense = expense_category.sort_values("Amount",ascending=False).iloc[0]
    expense_pct = float(largest_expense["Amount"])/revenue*100
    add_rec("Medium","Cost control",f"{largest_expense['Expense_Category']} is the largest expense category at ₹{float(largest_expense['Amount']):,.0f} ({expense_pct:.1f}% of revenue).",
            "Break the expense into controllable and committed components; benchmark month-to-month and review approvals without assuming the cost is excessive.",
            "Expense as % of revenue; monthly variance","Within 30 days")

if not recommendations:
    add_rec("Low","Monitoring","No rule-based priority issue was triggered by the current filtered dataset.",
            "Continue monthly monitoring and investigate any emerging variance from budget, forecast or historical trend.",
            "Revenue, margin, receivables ageing, inventory status","Monthly")

# Sort recommendations by severity
priority_order = {"Critical":0,"High":1,"Medium":2,"Low":3}
recommendations = sorted(recommendations,key=lambda x:priority_order.get(x["Priority"],9))
st.subheader("Prioritized Management Recommendations")
rec_df = pd.DataFrame(recommendations)
st.dataframe(rec_df,hide_index=True,use_container_width=True)

st.subheader("Management Action Tracker")
tracker = rec_df[["Priority","Area","Recommended Management Action","Suggested KPI","Timeframe"]].copy()
tracker["Status"] = "Not Started"
tracker["Management Owner"] = ""
st.dataframe(tracker,hide_index=True,use_container_width=True)
st.download_button("Download Management Action Plan (CSV)", tracker.to_csv(index=False).encode("utf-8"),
                   file_name="FinSight_Management_Action_Plan.csv",mime="text/csv")



st.header("🤖 FinSight AI Analyst")
st.caption("Answers are generated locally using Ollama and the Qwen model, grounded in the currently filtered dashboard data.")

# Build a compact, calculated context. Python performs the calculations; the LLM explains them.
monthly_context = monthly.sort_values("Month").to_dict(orient="records") if not monthly.empty else []
category_context = category.sort_values("Revenue", ascending=False).to_dict(orient="records") if not category.empty else []
expense_context = expense_category.to_dict(orient="records") if not expense_category.empty else []
receivables_context = ar_summary.to_dict(orient="records") if not ar_summary.empty else []
alert_context = alerts[[c for c in alerts.columns if c in ["Product_ID", "Product_Name", "Current_Stock", "Reorder_Level", "Stock_Status"]]].to_dict(orient="records") if not alerts.empty else []

# Independent validation metrics calculated in Python (not by the LLM)
expense_breakdown_total = float(expense_category["Amount"].sum()) if not expense_category.empty else 0.0
expense_reconciliation_difference = float(opex - expense_breakdown_total)
ar_total = float(ar["Outstanding_Balance"].sum()) if not ar.empty else 0.0
ar_90_plus = float(ar.loc[ar["Days_Outstanding"] > 90, "Outstanding_Balance"].sum()) if not ar.empty else 0.0
ar_over_60 = float(ar.loc[ar["Days_Outstanding"] > 60, "Outstanding_Balance"].sum()) if not ar.empty else 0.0
ar_90_plus_pct = ar_90_plus / ar_total * 100 if ar_total else 0.0
ar_over_60_pct = ar_over_60 / ar_total * 100 if ar_total else 0.0

# Monthly and category ratios are computed in Python and passed as ready-to-use metrics.
monthly["Gross_Margin_%"] = np.where(monthly["Revenue"] != 0, monthly["Gross_Profit"] / monthly["Revenue"] * 100, 0)
monthly["Operating_Margin_%"] = np.where(monthly["Revenue"] != 0, monthly["Operating_Profit"] / monthly["Revenue"] * 100, 0)
monthly_context = monthly.sort_values("Month").to_dict(orient="records") if not monthly.empty else []
category_context = category.sort_values("Revenue", ascending=False).to_dict(orient="records") if not category.empty else []
expense_context = expense_category.to_dict(orient="records") if not expense_category.empty else []
receivables_context = ar_summary.to_dict(orient="records") if not ar_summary.empty else []
alert_context = alerts[[c for c in alerts.columns if c in ["Product_ID", "Product_Name", "Current_Stock", "Reorder_Level", "Stock_Status"]]].to_dict(orient="records") if not alerts.empty else []

financial_context = {
    "period_selected": f"{start_date.date()} to {end_date.date()}",
    "filters": {"categories": selected_categories, "regions": selected_regions},
    "kpis": {
        "revenue_inr": round(float(revenue), 2),
        "cogs_inr": round(float(cogs), 2),
        "gross_profit_inr": round(float(gp), 2),
        "gross_margin_percent": round(float(gm), 4),
        "operating_expenses_inr": round(float(opex), 2),
        "operating_profit_inr": round(float(op_profit), 2),
        "operating_margin_percent": round(float(om), 4),
        "transaction_count": int(txn),
        "average_transaction_value_inr": round(float(atv), 2),
    },
    "expense_validation": {
        "operating_expenses_total_from_expense_sheet_inr": round(float(opex), 2),
        "sum_of_expense_category_totals_inr": round(float(expense_breakdown_total), 2),
        "reconciliation_difference_inr": round(float(expense_reconciliation_difference), 2),
        "reconciles_within_1_rupee": bool(abs(expense_reconciliation_difference) <= 1.0),
    },
    "receivables_validation": {
        "total_receivables_inr": round(ar_total, 2),
        "receivables_90_plus_days_inr": round(ar_90_plus, 2),
        "receivables_90_plus_percent_of_total": round(ar_90_plus_pct, 4),
        "receivables_over_60_days_inr": round(ar_over_60, 2),
        "receivables_over_60_percent_of_total": round(ar_over_60_pct, 4),
    },
    "monthly_results": monthly_context,
    "category_results": category_context,
    "expense_breakdown": expense_context,
    "receivables_ageing": receivables_context,
    "inventory_reorder_alerts": alert_context,
}

# Add Python-generated anomaly flags to the AI context.
anomaly_context = detected[["Month", "Anomaly_Flags"]].to_dict(orient="records") if "detected" in locals() and not detected.empty else []
financial_context["anomaly_flags"] = anomaly_context
financial_context["forecasting"] = forecast_context
financial_context["scenario_analysis"] = scenario_context

# Visible audit panel: users can see whether Python totals reconcile.
st.subheader("Financial Accuracy Audit")
a1, a2, a3 = st.columns(3)
a1.metric("Expense-sheet total", f"₹{opex:,.2f}")
a2.metric("Sum of expense categories", f"₹{expense_breakdown_total:,.2f}")
a3.metric("Reconciliation difference", f"₹{expense_reconciliation_difference:,.2f}")
if abs(expense_reconciliation_difference) <= 1.0:
    st.success("Expense totals reconcile: Python confirms the category total matches the expense-sheet total.")
else:
    st.warning("Expense totals do not reconcile. Review the source workbook or filters before relying on the analysis.")
st.caption(f"Receivables audit: total ₹{ar_total:,.2f} | 90+ days ₹{ar_90_plus:,.2f} ({ar_90_plus_pct:.2f}% of total). Calculated directly from the Receivables sheet.")

system_prompt = f"""You are FinSight AI, a careful financial analyst and business decision-support assistant.
Python is the authoritative calculator. Use ONLY the financial context supplied below for factual claims about this business.
STRICT FINANCIAL ACCURACY RULES:
1. Do not invent, estimate, or independently calculate totals when Python provides the exact figure. Copy the supplied value.
2. When asked for total expenses, use kpis.operating_expenses_inr and expense_validation.operating_expenses_total_from_expense_sheet_inr. Do not add category figures yourself.
3. When discussing expense categories, use expense_breakdown exactly as supplied. Never change decimal placement or scale (e.g., lakh to crore).
4. When discussing receivables, use receivables_validation totals and percentages. Do not sum ageing buckets yourself.
5. If a supplied reconciliation check is false, disclose the discrepancy and do not claim the totals reconcile.
6. Never invent data, causes, customer sentiment, footfall, market conditions, or operational details that are not in the context.
7. Distinguish facts from hypotheses. If data cannot establish a cause, state what additional data is needed.
8. Compare like with like: months with months, categories with categories, and regions with regions.
9. For percentages, use Python-supplied percentages. If a percentage is not supplied, clearly show the formula and use only the figures provided; otherwise say the data is insufficient.
10. Recommendations must cite a specific metric from the context and explain the connection. Avoid unsupported claims.
11. Use INR (₹), never USD/dollars, unless the user explicitly asks for a currency conversion. Use Indian number formatting and lakh/crore where practical; preserve exact supplied values.
12. For forecasts or scenarios, label them illustrative and state assumptions.
13. If asked to audit a previous answer, acknowledge specific mistakes and correct them using the supplied Python figures; do not defend an incorrect answer.
14. Treat anomaly_flags as rule-based alerts, not proof of causation. Explain the threshold/flag and recommend investigation; do not invent causes.
15. Forecasts are Python model outputs. Use supplied forecasting context exactly; never present forecasts as guaranteed or actual results.
16. Explain the selected model and backtest MAE/RMSE when relevant. Mention short-history and no-seasonality caveats.
17. When forecast error percentages are supplied, explain them as error relative to the holdout mean scale—not as accuracy or confidence. Avoid calling forecasts “accurate” or “reasonably close” solely from a small test sample.
18. The backtest uses an expanding training window and sequential one-step-ahead predictions. This reduces future-data leakage; do not incorrectly claim this method inherently causes overfitting. Highlight the small holdout sample as the main reliability limitation.
19. Forecasting output should clearly distinguish the model, historical forecast error, future forecast values, and uncertainty.
20. Scenario analysis is a user-controlled what-if simulation, not a prediction. Use scenario_analysis values exactly and describe the assumptions. Never infer causality.
21. Target operating margin revenue calculator assumes gross margin remains constant and scenario operating expenses remain fixed. State these assumptions when explaining the target.

FINANCIAL CONTEXT (JSON):
{financial_context}
"""

if "finsight_chat" not in st.session_state:
    st.session_state.finsight_chat = []

with st.expander("AI Analyst settings", expanded=False):
    ollama_model = st.text_input("Ollama model", value="qwen2.5:3b", key="finsight_model")
    st.write("Ollama must be running on this computer at http://localhost:11434.")

for message in st.session_state.finsight_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("Ask a question about the financial data shown above…")
if user_question:
    st.session_state.finsight_chat.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your financial data locally…"):
            try:
                import requests
                ollama_payload = {
                    "model": ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *st.session_state.finsight_chat[-8:],
                    ],
                    "stream": False,
                    "options": {"temperature": 0.2}
                }
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json=ollama_payload,
                    timeout=180
                )
                response.raise_for_status()
                answer = response.json().get("message", {}).get("content", "No response returned by the model.")
                st.markdown(answer)
            except requests.exceptions.ConnectionError:
                answer = "I couldn't connect to Ollama. Please ensure Ollama is running, then refresh/retry."
                st.error(answer)
            except requests.exceptions.Timeout:
                answer = "The model took too long to respond. Try a shorter question or wait and retry."
                st.error(answer)
            except Exception as exc:
                answer = f"Something went wrong while contacting Ollama: {exc}"
                st.error(answer)
    st.session_state.finsight_chat.append({"role": "assistant", "content": answer})

if st.button("Clear AI chat history"):
    st.session_state.finsight_chat = []
    st.rerun()

st.caption("AI responses can still contain mistakes. Verify important financial decisions against the underlying data.")

# ============================================================
# PHASE 9: EXECUTIVE REPORT GENERATOR
# ============================================================
st.divider()
st.header("📄 AI-Powered Executive Report Generator")
st.caption("Generate a downloadable PDF from the currently selected dashboard filters. Optional AI narrative uses local Ollama.")
use_ai_report = st.checkbox("Use local AI for executive narrative (Ollama required)", value=False, key="phase9_ai_narrative")
phase9_model = st.text_input("Ollama model", "qwen2.5:3b", key="phase9_model", disabled=not use_ai_report)


def phase9_narrative():
    # AI is asked for qualitative interpretation only; Python values remain authoritative.
    fallback = (f"For the selected period, revenue was ₹{revenue:,.0f}, gross profit was ₹{gp:,.0f} "
        f"({gm:.2f}% gross margin), and operating profit was ₹{op_profit:,.0f} ({om:.2f}% operating margin). ")
    if op_profit < 0:
        fallback += "The business recorded an operating loss; management should prioritize a recovery plan and review contribution margins and controllable costs. "
    elif om < 5:
        fallback += "Operating margin is below the prototype 5% screening threshold and should be reviewed. "
    if total_ar and aged_60/total_ar > .10:
        fallback += f"Receivables over 60 days total ₹{aged_60:,.0f} ({aged_60/total_ar*100:.1f}% of receivables), warranting an ageing-based collection review. "
    if len(alerts):
        fallback += f"{len(alerts)} inventory item(s) are at or below reorder level and should be reviewed against demand and supplier lead times. "
    fallback += "These observations use the uploaded synthetic dataset and current dashboard filters."
    if not use_ai_report:
        return fallback, "Rule-based summary"
    try:
        import requests, json, re
        context={"period":f"{start_date.date()} to {end_date.date()}",
            "financial_facts":["Revenue is positive","Gross margin is calculated from source data",
            "Operating profitability is calculated from source data"],
            "operating_profit_status":"profit" if op_profit>0 else "loss",
            "operating_margin_band":"below 5%" if om<5 else "5% to below 10%" if om<10 else "10% or more",
            "receivables_risk":"elevated" if total_ar and aged_60/total_ar>.10 else "not elevated by prototype threshold",
            "inventory_alert_count":int(len(alerts)),
            "recommendation_themes":[r.get("Area","") for r in recommendations]}
        prompt=("Write 4-5 concise sentences for a finance management executive summary. "
                "STRICT RULE: do not include ANY digits, numbers, percentages, currency amounts, dates, or numeric claims. "
                "Use qualitative interpretation only. Do not invent causes. Distinguish observed facts from suggestions. "
                "Mention the data is synthetic. Context: "+json.dumps(context,default=str))
        r=requests.post('http://localhost:11434/api/generate',json={"model":phase9_model,"prompt":prompt,"stream":False,"options":{"temperature":0.1}},timeout=90)
        r.raise_for_status()
        ai_text=r.json().get('response','').strip()
        # Strip Markdown and enforce the no-numbers policy to prevent incorrect financial figures.
        ai_text=re.sub(r'^\s*#+\s*','',ai_text,flags=re.MULTILINE)
        ai_text=re.sub(r'\*\*|__|`','',ai_text).strip()
        if ai_text and not re.search(r'\d|₹|%|[$]',ai_text):
            return ai_text, f"Local AI qualitative narrative ({phase9_model})"
        st.warning("AI narrative contained numeric claims and was rejected; using Python-verified narrative.")
    except Exception as exc:
        st.warning(f"AI narrative unavailable; using verified summary. {exc}")
    return fallback, "Python-verified fallback"
def phase9_pdf(summary, source):
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import re, os
    # Register Unicode font to support Indian rupee and other symbols.
    font_candidates=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/seguisym.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
    ]
    font_path=next((fp for fp in font_candidates if os.path.exists(fp)),None)
    font_name="Helvetica"
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("FinSightUnicode",font_path))
            font_name="FinSightUnicode"
        except Exception:
            pass
    buff=BytesIO()
    doc=SimpleDocTemplate(buff,pagesize=A4,leftMargin=14*mm,rightMargin=14*mm,topMargin=15*mm,bottomMargin=17*mm,title='FinSight AI Executive Report')
    ss=getSampleStyleSheet()
    ss.add(ParagraphStyle(name='FSHead',parent=ss['Heading1'],fontName=font_name,fontSize=13.5,leading=17,textColor=colors.HexColor('#173B5E'),spaceBefore=8,spaceAfter=5,keepWithNext=True))
    ss.add(ParagraphStyle(name='FSBody',parent=ss['BodyText'],fontName=font_name,fontSize=8.6,leading=12,spaceAfter=4))
    ss.add(ParagraphStyle(name='FSCell',parent=ss['BodyText'],fontName=font_name,fontSize=7.2,leading=9))
    ss.add(ParagraphStyle(name='FSCellBold',parent=ss['BodyText'],fontName=font_name,fontSize=7.2,leading=9))
    ss.add(ParagraphStyle(name='FSTitle',parent=ss['Title'],fontName=font_name,fontSize=21,leading=25,textColor=colors.HexColor('#173B5E'),spaceAfter=5))
    ss.add(ParagraphStyle(name='FSNote',parent=ss['BodyText'],fontName=font_name,fontSize=7.2,leading=9,textColor=colors.HexColor('#5D6D7E')))
    story=[]
    def para(txt,style='FSBody'):
        # Convert markdown emphasis to readable HTML emphasis, then escape remaining unsafe text.
        txt=str(txt)
        txt=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',txt)
        txt=re.sub(r'\*(.*?)\*',r'<i>\1</i>',txt)
        txt=txt.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        txt=txt.replace('&lt;b&gt;','<b>').replace('&lt;/b&gt;','</b>').replace('&lt;i&gt;','<i>').replace('&lt;/i&gt;','</i>')
        return Paragraph(txt,ss[style])
    def make_table(rows,widths=None):
        cells=[]
        for ridx,row in enumerate(rows):
            cells.append([para(str(c),'FSCellBold' if ridx==0 else 'FSCell') for c in row])
        t=Table(cells,colWidths=widths,repeatRows=1,hAlign="LEFT")
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173B5E')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#CFD8E3')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FA')]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        return t
    def footer(canvas,d):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor('#D7E0E8'))
        canvas.line(14*mm,12*mm,A4[0]-14*mm,12*mm); canvas.setFont(font_name,7)
        canvas.setFillColor(colors.HexColor('#64748B'))
        canvas.drawString(14*mm,8*mm,'FinSight AI | Prototype | Synthetic data — not real company information')
        canvas.drawRightString(A4[0]-14*mm,8*mm,f'Page {d.page}'); canvas.restoreState()
    def make_chart(fig):
        import matplotlib.pyplot as plt
        image_buffer=BytesIO()
        fig.tight_layout()
        fig.savefig(image_buffer,format="png",dpi=150,bbox_inches="tight")
        plt.close(fig); image_buffer.seek(0)
        return Image(image_buffer,width=165*mm,height=78*mm)
    story += [para('FinSight AI','FSTitle'),para('Executive Financial Intelligence Report','FSHead'),
        para(f'Reporting period: {start_date.date()} to {end_date.date()} | Generated: {pd.Timestamp.now().strftime("%d %b %Y %H:%M")}','FSNote'),
        para('Dataset: Synthetic Nova Retail Pvt. Ltd. | Current dashboard filters applied.','FSNote'),Spacer(1,5)]
    story += [para('Executive Summary','FSHead'),para(summary),para(f'Narrative source: {source}. Financial values in this report are generated by Python from the uploaded dataset.','FSNote')]
    story += [para('Financial KPI Scorecard','FSHead'),make_table([['Metric','Value'],['Revenue',f'₹{revenue:,.0f}'],['Gross Profit',f'₹{gp:,.0f}'],['Gross Margin',f'{gm:.2f}%'],['Operating Expenses',f'₹{opex:,.0f}'],['Operating Profit',f'₹{op_profit:,.0f}'],['Operating Margin',f'{om:.2f}%'],['Transactions',f'{txn:,}'],['Average Transaction Value',f'₹{atv:,.0f}']],[78*mm,87*mm])]
    story += [para('Financial Health & Data Quality','FSHead'),make_table([['Indicator','Result'],['Financial Health Score',f'{health_score}/100 — {health_label}'],['Expense reconciliation difference',f'₹{(float(opex)-(float(expense_category["Amount"].sum()) if not expense_category.empty else 0.0)):,.2f}'],['Receivables total',f'₹{total_ar:,.0f}'],['Receivables >60 days',f'₹{aged_60:,.0f} ({aged_60/total_ar*100:.1f}%)' if total_ar else 'N/A'],['Receivables >90 days',f'₹{ar_90_plus:,.0f} ({ar_90_plus_pct:.1f}%)' if total_ar else 'N/A'],['Inventory alerts',str(len(alerts))]],[78*mm,87*mm])]
    story.append(para('Revenue & Category Performance','FSHead'))
    if not category.empty:
        rows=[['Category','Revenue','Gross Profit','GM %']]
        for _,r0 in category.sort_values('Revenue',ascending=False).head(10).iterrows():
            rows.append([str(r0.get('Category','')),f'₹{r0.get("Revenue",0):,.0f}',f'₹{r0.get("Gross_Profit",0):,.0f}',f'{r0.get("Gross_Margin_%",0):.1f}%'])
        story.append(make_table(rows,[42*mm,43*mm,43*mm,34*mm]))
        try:
            import matplotlib.pyplot as plt
            cats=category.sort_values("Gross_Margin_%",ascending=True).tail(10)
            fig,ax=plt.subplots(figsize=(8,3.6)); ax.barh(cats["Category"].astype(str),cats["Gross_Margin_%"])
            ax.set_xlabel("Gross Margin (%)"); ax.set_title("Category Gross Margin Comparison")
            story.append(make_chart(fig))
        except Exception as chart_err:
            story.append(para(f'Category chart unavailable: {chart_err}','FSNote'))
    story.append(para('Monthly Financial Trend','FSHead'))
    if not monthly.empty:
        rows=[['Month','Revenue','Gross Profit','Operating Profit']]
        for _,m0 in monthly.sort_values('Month').iterrows():
            rows.append([str(m0['Month']),f'₹{m0.get("Revenue",0):,.0f}',f'₹{m0.get("Gross_Profit",0):,.0f}',f'₹{m0.get("Operating_Profit",0):,.0f}'])
        story.append(make_table(rows,[32*mm,44*mm,44*mm,42*mm]))
        try:
            import matplotlib.pyplot as plt
            trend=monthly.sort_values("Month")
            fig,ax=plt.subplots(figsize=(8,3.6)); ax.plot(trend["Month"],trend["Revenue"],marker="o")
            ax.set_title("Monthly Revenue Trend"); ax.set_ylabel("Revenue (₹)"); ax.tick_params(axis="x",rotation=45)
            story.append(make_chart(fig))
        except Exception as chart_err:
            story.append(para(f'Revenue chart unavailable: {chart_err}','FSNote'))
    story.append(para('Expense Analysis','FSHead'))
    if not expense_category.empty:
        rows=[['Expense Category','Amount','Share of Opex']]
        for _,e0 in expense_category.sort_values('Amount',ascending=False).iterrows():
            rows.append([str(e0['Expense_Category']),f'₹{e0["Amount"]:,.0f}',f'{e0["Amount"]/opex*100:.1f}%' if opex else 'N/A'])
        story.append(make_table(rows,[65*mm,55*mm,45*mm]))
    story.append(para('Receivables & Inventory','FSHead'))
    story.append(para(f'Receivables total ₹{total_ar:,.0f}; over 60 days ₹{aged_60:,.0f} ({aged_60/total_ar*100:.1f}%); over 90 days ₹{ar_90_plus:,.0f} ({ar_90_plus_pct:.1f}%).' if total_ar else 'Receivables unavailable.'))
    if len(alerts):
        rows=[['Product','Stock','Reorder level','Status']]
        for _,a0 in alerts.iterrows(): rows.append([str(a0.get('Product_Name','')),str(a0.get('Current_Stock','')),str(a0.get('Reorder_Level','')),str(a0.get('Stock_Status','Review'))])
        story.append(make_table(rows,[55*mm,35*mm,35*mm,40*mm]))
    else: story.append(para('No reorder alerts detected in current selection.'))
    story.append(para('Financial Anomaly Flags','FSHead'))
    if anomaly_context:
        rows=[['Month','Flag']]+[[str(a.get('Month','')),str(a.get('Anomaly_Flags',''))] for a in anomaly_context]
        story.append(make_table(rows,[35*mm,130*mm]))
    else: story.append(para('No anomaly flags available for the selected period.'))
    story.append(para('Forecast Outlook','FSHead'))
    fc=forecast_context if isinstance(forecast_context,dict) else {}; metrics=fc.get('metrics',{})
    if metrics:
        for name,details in metrics.items():
            mae=details.get('mae'); rmse=details.get('rmse')
            rmae=details.get('mae_percent_of_holdout_mean', details.get('relative_mae_percent'))
            rrmse=details.get('rmse_percent_of_holdout_mean', details.get('relative_rmse_percent'))
            reliability="Weak" if (rmae is not None and float(rmae)>25) else "Moderate" if rmae is not None and float(rmae)>10 else "Lower relative error (limited backtest)" if rmae is not None else "Not assessed"
            story.append(para(f'<b>{name}</b> — selected model: {details.get("best_model",details.get("selected_model","N/A"))}. MAE: {f"₹{float(mae):,.0f}" if mae is not None else "N/A"}; RMSE: {f"₹{float(rmse):,.0f}" if rmse is not None else "N/A"}. Relative MAE: {f"{float(rmae):.2f}%" if rmae is not None else "N/A"}; relative RMSE: {f"{float(rrmse):.2f}%" if rrmse is not None else "N/A"}. Reliability screening: {reliability}; based on {details.get("test_observations",0)} holdout observation(s).','FSBody'))
            vals=details.get('forecast_values',[])
            dates=details.get('forecast_dates',[])
            if vals:
                rows=[['Forecast Month','Forecast Value']]+[[str(dates[i]) if i<len(dates) else f'Period {i+1}',f'₹{float(v):,.0f}'] for i,v in enumerate(vals)]
                story.append(make_table(rows,[75*mm,90*mm]))
    else: story.append(para('Forecast model outputs unavailable for this filter selection.'))
    story += [para('Scenario Analysis','FSHead'),para('Illustrative user-selected what-if assumptions—not a forecast.'),make_table([['Metric','Baseline','Scenario'],['Revenue',f'₹{base_revenue:,.0f}',f'₹{scenario_revenue:,.0f}'],['Gross Profit',f'₹{base_gross_profit:,.0f}',f'₹{scenario_gross_profit:,.0f}'],['Operating Expenses',f'₹{base_opex:,.0f}',f'₹{scenario_opex:,.0f}'],['Operating Profit',f'₹{base_operating_profit:,.0f}',f'₹{scenario_operating_profit:,.0f}'],['Operating Margin',f'{om:.2f}%',f'{scenario_operating_margin:.2f}%']],[55*mm,55*mm,55*mm]),para(f'Assumptions: revenue {scenario_revenue_change:+}%; gross margin {scenario_margin_change_pp:+.2f} pp; non-salary Opex {scenario_opex_change:+}%; salaries {scenario_salary_change:+}%.','FSNote')]
    try:
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(7,3.2)); labels=["Revenue","Gross Profit","Opex","Operating Profit"]
        baseline=[base_revenue,base_gross_profit,base_opex,base_operating_profit]
        scen=[scenario_revenue,scenario_gross_profit,scenario_opex,scenario_operating_profit]
        x=np.arange(len(labels)); width=.36
        ax.bar(x-width/2,baseline,width,label="Baseline"); ax.bar(x+width/2,scen,width,label="Scenario")
        ax.set_xticks(x,labels); ax.set_ylabel("INR"); ax.set_title("Baseline vs Scenario"); ax.legend()
        story.append(make_chart(fig))
    except Exception as chart_err:
        story.append(para(f'Scenario chart unavailable: {chart_err}','FSNote'))
    story.append(para('Management Recommendations','FSHead'))
    if recommendations:
        rows=[['Priority','Area','Finding','Recommended Action','KPI','Timeframe']]
        for rec in recommendations: rows.append([rec['Priority'],rec['Area'],rec['Evidence / Finding'],rec['Recommended Management Action'],rec['Suggested KPI'],rec['Timeframe']])
        story.append(make_table(rows,[18*mm,24*mm,34*mm,49*mm,23*mm,17*mm]))
    story += [para('Conclusion & Limitations','FSHead'),para('This report uses synthetic demonstration data and current dashboard filters. Health-score weights and thresholds are prototype heuristics, not industry benchmarks. Forecasts are indicative and based on limited history; scenario analysis is a user-defined simulation. Verify the source data and assumptions before making decisions.')]
    doc.build(story,onFirstPage=footer,onLaterPages=footer); buff.seek(0); return buff.getvalue()

if st.button('Generate Executive Financial Report PDF',type='primary',key='phase9_generate'):
    with st.spinner('Building report...'):
        narrative, narrative_source=phase9_narrative()
        try:
            st.session_state['phase9_pdf']=phase9_pdf(narrative,narrative_source)
            st.session_state['phase9_filename']=f"FinSight_Executive_Report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.success('Report generated successfully.')
        except Exception as report_exc:
            st.error(f'PDF generation failed: {report_exc}')
if st.session_state.get('phase9_pdf'):
    st.download_button('⬇️ Download Executive Financial Report (PDF)',st.session_state['phase9_pdf'],file_name=st.session_state.get('phase9_filename','FinSight_Executive_Report.pdf'),mime='application/pdf',key='phase9_download')



