# FinSight AI — Financial & Analytical Methodology

## 1. Financial Performance Metrics

### Revenue

Revenue represents the total value of sales generated during the selected period.

Revenue = Sum of Sales Revenue

### Gross Profit

Gross Profit measures revenue remaining after deducting the cost of goods sold.

Gross Profit = Revenue − Cost of Goods Sold

### Gross Margin

Gross Margin measures gross profit as a percentage of revenue.

Gross Margin (%) = (Gross Profit / Revenue) × 100

### Operating Expenses

Operating Expenses represent expenses incurred in operating the business, excluding the cost of goods sold.

### Operating Profit

Operating Profit measures profitability after operating expenses.

Operating Profit = Gross Profit − Operating Expenses

### Operating Margin

Operating Margin represents operating profit as a percentage of revenue.

Operating Margin (%) = (Operating Profit / Revenue) × 100

---

## 2. Expense Analysis

Expenses are aggregated by category to identify:

- Major cost contributors
- Expense concentration
- Changes in spending
- Potential areas for cost control

Expense reconciliation compares the total recorded in the expense dataset with the sum of category-level expenses.

Reconciliation Difference = Expense Sheet Total − Category Expense Total

A difference of zero indicates that the totals reconcile.

---

## 3. Receivables Analysis

Receivables represent amounts owed to the business by customers.

The analysis evaluates:

- Total outstanding receivables
- Ageing of receivables
- Amount overdue
- Receivables outstanding for 90 days or more

90+ Days Receivables Percentage:

(Receivables Outstanding for 90+ Days / Total Receivables) × 100

Higher overdue receivables may indicate increased collection risk and potential pressure on cash flow.

---

## 4. Inventory Risk Analysis

Inventory is evaluated using available stock and reorder-level information.

Products with stock at or below their reorder threshold are flagged for review.

The alert indicates a potential replenishment requirement and does not automatically account for demand forecasts, supplier lead times, or purchase constraints.

---

## 5. Anomaly Detection

The application uses rule-based anomaly detection to flag unusual financial patterns.

### Operating Loss

Operating profit below zero.

### Revenue Decline

Month-over-month revenue decline exceeding the configured threshold.

### Expense Increase

Month-over-month operating expense increase exceeding the configured threshold.

### Gross Margin Deterioration

Gross margin significantly below the selected-period reference level.

Anomaly flags are intended to support investigation. They do not independently establish the underlying cause.

---

## 6. Forecasting Methods

### Moving Average

The moving average forecast uses the average of recent observations.

Forecast = Average of Recent Period Values

It is useful for smoothing short-term fluctuations.

### Linear Trend

Linear trend forecasting estimates the relationship between time and the observed financial metric.

The model projects the estimated trend into future periods.

### Holt's Linear Trend

Holt's Linear Trend method uses:

- Level
- Trend

It is designed for data with a trend and does not explicitly model seasonality.

---

## 7. Forecast Evaluation

Forecast performance is evaluated using historical holdout observations.

### Mean Absolute Error (MAE)

MAE measures the average absolute difference between actual and forecast values.

MAE = Mean(|Actual − Forecast|)

### Root Mean Squared Error (RMSE)

RMSE measures the square root of the average squared forecast errors.

RMSE = √Mean((Actual − Forecast)²)

RMSE places greater weight on larger forecast errors.

### Relative Forecast Error

Relative error metrics express forecasting errors in relation to a reference scale, making errors easier to interpret.

Forecast reliability assessments should be interpreted cautiously when the backtesting sample is small.

---

## 8. Scenario Analysis

The What-If Simulator evaluates the financial impact of user-defined assumptions.

Variables include:

- Revenue percentage change
- Gross margin percentage-point change
- Operating expense percentage change
- Salary expense percentage change

Scenario results are calculated using the modified assumptions.

The model is designed to demonstrate sensitivity analysis and decision support.

Scenario results are illustrative and should not be interpreted as guaranteed future outcomes.

---

## 9. AI-Assisted Financial Interpretation

The AI component interprets financial metrics calculated by the Python analytics engine.

The system aims to distinguish:

- Calculated facts
- Observed trends
- Potential explanations
- Recommendations
- Limitations

The AI does not replace the programmatic financial calculation engine.

AI-generated conclusions should be reviewed before being used in actual business decisions.

---

## 10. Limitations

- The dataset is synthetic.
- Historical observations are limited.
- Forecast accuracy varies by metric.
- Backtesting sample size is limited.
- Scenario modelling uses simplified assumptions.
- Anomaly detection identifies patterns requiring investigation rather than proven causes.
- AI interpretations may require human validation.
