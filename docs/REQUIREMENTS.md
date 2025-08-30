# Finance Assistant – Requirements

## Phase 1 – MVP (Core, must finish in <6h)

- [ ] Parse PDF text (pdfplumber / OCR if scanned).
- [ ] Parse CSV bank files (pandas).
- [ ] AI-assisted parsing (LLM → JSON).
- [ ] Store transactions in PostgreSQL with JSONB column.
- [ ] Dashboard with:
  - Total income/expenses.
  - Expenses by category (pie chart).
  - Monthly trends (line chart).

## Phase 2 – Enhanced Features

- [ ] Auto-categorization of transactions with AI.
- [ ] Recurring expense detection (subscriptions, rent).
- [ ] Anomaly detection (outlier spends).
- [ ] Forecast next month’s expenses (Prophet or statsmodels).
- [ ] Export categorized data to CSV/Excel.

## Phase 3 – Wow Factor (Optional if time)

- [ ] Natural language queries:
  - "How much did I spend on coffee in July?"
- [ ] Personalized insights:
  - "Your delivery spend this year = new iPhone."
- [ ] Financial health score (fixed vs variable ratio).
- [ ] Carbon footprint estimate from categories.
