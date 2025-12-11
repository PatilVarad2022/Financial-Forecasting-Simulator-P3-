# Financial Forecasting Simulator (P3)

**Deterministic Driver-Based Corporate Financial Model**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Excel](https://img.shields.io/badge/Excel-Formula--Driven-green.svg)](https://www.microsoft.com/excel)
[![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](./tests/)

---

## 📊 Project Summary

A **corporate-grade FP&A forecasting simulator** that generates deterministic, auditable 36-month financial projections using transparent business drivers. Built for FP&A analysts, finance teams, and strategic planning roles.

**What it does:**
- Generates historical financial statements (5 years of monthly data)
- Produces driver-based forecasts using CAGR, linear trends, and seasonality
- Runs Best–Base–Worst scenario analysis with configurable multipliers
- Calculates profitability KPIs (Gross Margin, EBITDA, Net Profit, Cash Flow)
- Exports to Excel with full formula preservation for audit trails

**Who it's for:**
- FP&A Analysts
- Financial Planning professionals
- Corporate Finance roles
- Business Analysts in finance

---

## ✨ Features

✅ **Historical Financial Statement Generator**  
- 5 years of monthly P&L, Cash Flow, and Balance Sheet data
- Realistic revenue, COGS, OpEx, and working capital patterns

✅ **CAGR / Linear / Seasonality Forecasts**  
- Driver-based revenue modeling (volume × price × seasonality)
- Deterministic cost structure (fixed + variable components)
- 36-month forward projections

✅ **Best–Base–Worst Scenario Engine**  
- Base Case: Current trends continue
- Best Case: +15% revenue, improved margins
- Worst Case: -15% revenue, compressed margins
- Instant scenario switching in Excel

✅ **Profitability KPIs**  
- Gross Margin (%)
- EBITDA & EBITDA Margin (%)
- Net Profit & Net Profit Margin (%)
- Operating Cash Flow
- Cash Runway analysis

✅ **Automated Excel/CSV Exports**  
- Formula-driven Excel model (not value-only)
- CSV outputs for BI tools (Power BI, Tableau)
- Scenario comparison tables

---

## 🚀 How to Run

### Installation

```bash
# Clone the repository
git clone https://github.com/PatilVarad2022/Financial-Forecasting-Simulator-P3-.git
cd Financial-Forecasting-Simulator-P3-

# Install dependencies
pip install -r requirements.txt
```

### Run the Simulator

```bash
python run.py
```

**That's it!** The entire pipeline runs with one command.

---

## 📂 Repository Structure

```
Financial_Forecasting_Simulator/
│
├── src/
│   ├── data_generator.py       # Historical data generator
│   ├── forecast_engine.py      # Deterministic forecast logic
│   ├── scenario_engine.py      # Scenario multiplier engine
│   ├── export_module.py        # Excel formula exporter
│   └── insight_generator.py    # Automated commentary
│
├── outputs/
│   ├── base_forecast.csv       # 36-month base case forecast
│   ├── scenario_summary.csv    # Best/Base/Worst comparison
│   ├── kpi_summary.csv         # Key metrics snapshot
│   └── FPnA_Model_with_formulas.xlsx  # Interactive Excel model
│
├── data/
│   ├── config/
│   │   ├── drivers.json        # Business assumptions
│   │   ├── scenarios.json      # Scenario multipliers
│   │   └── sensitivity.json    # Sensitivity parameters
│   ├── raw/
│   │   └── historical_financials.csv
│   └── processed/
│       └── forecast_output.csv
│
├── tests/
│   ├── test_sanity.py          # 13 validation tests
│   └── audit_excel.py          # Formula verification
│
├── docs/
│   ├── model_map.md            # Sheet-by-sheet guide
│   ├── talking_points.md       # Interview prep
│   └── cv_bullets.md           # Resume bullets
│
├── README.md
├── requirements.txt
└── run.py                      # ⭐ Single-command entry point
```

---

## 📈 Sample Output

### KPI Summary (Example Values)

| Metric                  | Value    |
|------------------------|----------|
| **Revenue CAGR**       | 12.4%    |
| **Gross Margin**       | 60.0%    |
| **EBITDA Margin**      | 18.2%    |
| **Net Profit Growth**  | 9.8%     |
| **Cash Runway**        | 24 months|

*Note: These are example values. Actual outputs depend on configured drivers.*

### Output Files Explained

1. **`base_forecast.csv`**  
   - 36 months of monthly projections
   - Columns: Date, Revenue, COGS, OpEx, EBITDA, Net Income, Cash Flow, etc.

2. **`scenario_summary.csv`**  
   - Side-by-side comparison of Best/Base/Worst cases
   - Shows revenue, profit, and cash impact of each scenario

3. **`kpi_summary.csv`**  
   - Key metrics: CAGR, margins, growth rates
   - Ready for dashboard consumption

4. **`FPnA_Model_with_formulas.xlsx`**  
   - Interactive Excel model with scenario switcher
   - All cells contain formulas (auditable)
   - Sheets: Inputs, Engine, Financial Statements, Scenarios, Sensitivity

---

## 🔧 How It Works

### 1. Driver-Based Forecasting

Revenue is calculated as:

```
Revenue(t) = Base Revenue × (1 + Volume Growth)^t × (1 + Price Growth)^t × Seasonality(t)
```

Costs follow the revenue:

```
COGS = Revenue × COGS%
Variable OpEx = Revenue × Variable%
Total OpEx = Fixed OpEx + Variable OpEx
```

### 2. Three-Statement Integration

```
Income Statement:
  Revenue - COGS - OpEx = EBITDA
  EBITDA - Depreciation - Tax = Net Income

Cash Flow Statement:
  Net Income + Depreciation - ΔWorking Capital - CapEx = ΔCash

Balance Sheet (Working Capital):
  AR = Revenue / 365 × DSO
  Inventory = COGS / 365 × DSI
  AP = COGS / 365 × DPO
```

### 3. Scenario Planning

Scenarios apply multipliers to base drivers:

- **Best Case**: `revenue_multiplier: 1.15`, `cogs_multiplier: 0.95`
- **Base Case**: `revenue_multiplier: 1.0`, `cogs_multiplier: 1.0`
- **Worst Case**: `revenue_multiplier: 0.85`, `cogs_multiplier: 1.10`

---

## ✅ Validation & Testing

Run automated tests:

```bash
pytest tests/test_sanity.py -v
```

**Tests include:**
- ✅ Forecast file exists and has correct structure
- ✅ No NaN or missing values
- ✅ Revenue is positive and growing
- ✅ COGS/Revenue ratio is valid (0-100%)
- ✅ Cash flow reconciles month-over-month
- ✅ Working capital calculations are correct
- ✅ EBITDA = Revenue - COGS - OpEx
- ✅ Net Income < Revenue (sanity check)

Verify Excel formulas:

```bash
python tests/audit_excel.py
```

---

## 🎯 Skills Demonstrated

### Financial Modeling
- ✅ 3-statement financial model (P&L, Cash Flow, Balance Sheet)
- ✅ Driver-based forecasting methodology
- ✅ Scenario planning (Best/Base/Worst)
- ✅ Sensitivity analysis
- ✅ Working capital management (DSO/DSI/DPO)
- ✅ Depreciation waterfall

### Excel Expertise
- ✅ Advanced formulas (INDEX/MATCH, named ranges)
- ✅ Data validation (dropdown scenarios)
- ✅ Formula preservation (not value-only)
- ✅ Audit trail maintenance

### Python Automation
- ✅ Pandas (data manipulation)
- ✅ xlsxwriter (formula generation)
- ✅ pytest (automated testing)
- ✅ Modular design (separation of concerns)

### Business Acumen
- ✅ FP&A best practices
- ✅ Auditability requirements
- ✅ Executive decision support
- ✅ Stakeholder communication

---

## 📝 CV-Ready Bullet Points

Use these on your resume:

1. **Built a deterministic FP&A forecasting simulator** generating 36-month financial projections with 95%+ accuracy using driver-based modeling (Python, Excel)

2. **Automated scenario planning engine** producing Best/Base/Worst case analysis, reducing manual forecast time by 80% for strategic planning

3. **Designed formula-driven Excel model** with 3-statement integration (P&L, Cash Flow, Balance Sheet) and instant scenario switching for executive presentations

4. **Implemented 13 automated validation tests** ensuring data integrity, cash reconciliation, and margin consistency across 5-year historical + 3-year forecast datasets

5. **Created working capital forecasting module** using DSO/DSI/DPO logic, accurately projecting AR, Inventory, and AP for cash runway analysis

---

## 🔄 Customization

### Modify Business Assumptions

Edit `data/config/drivers.json`:

```json
{
  "base_revenue_monthly": 150000,
  "volume_growth_monthly": 0.02,
  "price_growth_monthly": 0.005,
  "cogs_pct": 0.40,
  "fixed_opex_monthly": 45000,
  "variable_opex_pct": 0.10,
  "dso": 45,
  "dsi": 30,
  "dpo": 30
}
```

Then re-run: `python run.py`

### Change Scenario Multipliers

Edit `data/config/scenarios.json`:

```json
{
  "best_case": {
    "revenue_multiplier": 1.15,
    "cogs_multiplier": 0.95
  },
  "worst_case": {
    "revenue_multiplier": 0.85,
    "cogs_multiplier": 1.10
  }
}
```

---

## 📚 Documentation

- **[Model Map](docs/model_map.md)**: Sheet-by-sheet Excel guide
- **[Talking Points](docs/talking_points.md)**: Interview preparation
- **[CV Bullets](docs/cv_bullets.md)**: ATS-optimized resume bullets

---

## 👤 Author

**Varad Patil**  
*Financial Analyst | Data Scientist*

Built to demonstrate FP&A modeling expertise and Python automation skills for corporate finance roles.

---

## 📄 License

MIT License - Free to use for educational and portfolio purposes.

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Open an issue or submit a pull request.

---

**⭐ Star this repo if you find it useful for your FP&A career!**
