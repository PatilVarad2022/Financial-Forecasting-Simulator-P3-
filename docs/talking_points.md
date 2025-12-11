# Talking Points - P3 FP&A Forecasting Simulator

## For Interviews & Presentations

---

## 1. THE PROBLEM

### Business Context
"Most financial forecasting tools rely on black-box machine learning models that produce numbers analysts can't audit or explain to stakeholders. When a CFO asks 'why did revenue increase 12%?', you can't say 'the algorithm decided.'"

### Technical Challenge
"I needed to build a corporate-grade FP&A model that was:
- **Auditable**: Every number traces to a formula
- **Deterministic**: Same inputs → same outputs
- **Transparent**: Business logic visible to non-technical users
- **Dynamic**: Scenario switching without rebuilding"

### Why It Matters
"In FP&A roles, you're often presenting to boards and executives who need to understand the 'why' behind the numbers. A deterministic, driver-based model lets you say: 'Revenue grew because we assumed 2% monthly volume growth and 0.5% price increases, with 15% seasonality in Q4.'"

---

## 2. BUSINESS LOGIC

### Driver-Based Forecasting
"Instead of using ARIMA or Prophet to predict revenue, I built a formula:
```
Revenue = Base × (1 + Volume Growth)^t × (1 + Price Growth)^t × Seasonality
```
This means:
- **Volume Growth**: How many more units we sell each month
- **Price Growth**: Pricing power/inflation
- **Seasonality**: Q4 holiday bump, Q1 slowdown, etc."

### Three-Statement Integration
"The model automatically generates:
1. **Income Statement**: Revenue → COGS → OpEx → Net Income
2. **Cash Flow**: Operating CF + Investing CF = ΔCash
3. **Balance Sheet** (partial): AR, Inventory, AP, Cash

All linked—change one assumption, everything updates."

### Working Capital Logic
"I implemented DSO/DSI/DPO logic:
- **AR** = Revenue / 365 × Days Sales Outstanding
- **Inventory** = COGS / 365 × Days Sales Inventory
- **AP** = COGS / 365 × Days Payable Outstanding

This feeds into cash flow: ΔWC = (AR + Inv - AP)_current - (AR + Inv - AP)_prior"

---

## 3. KEY DRIVERS

### Revenue Drivers
- **Base Revenue**: $150K/month starting point
- **Volume Growth**: 2% monthly (compounding)
- **Price Growth**: 0.5% monthly (inflation/pricing power)
- **Seasonality**: 12-month array (85% in Jan, 140% in Dec)

### Cost Drivers
- **COGS**: 40% of revenue (variable)
- **Fixed OpEx**: $45K/month (rent, utilities, etc.)
- **Variable OpEx**: 10% of revenue (sales commissions, shipping)
- **Payroll**: Headcount × $6K/month average salary

### Capital Drivers
- **CapEx Schedule**: $50K in Mar, $75K in Sep, etc.
- **Depreciation**: Straight-line over 60 months
- **Useful Life**: 5 years for all assets

### Working Capital Drivers
- **DSO**: 45 days (how fast customers pay)
- **DSI**: 30 days (inventory turnover)
- **DPO**: 30 days (how fast we pay suppliers)

---

## 4. SCENARIOS

### Three Scenarios
1. **Base Case**: Current trends continue
   - Revenue Mult: 1.0×
   - COGS Mult: 1.0×
   
2. **Best Case**: Optimistic assumptions
   - Revenue Mult: 1.15× (+15%)
   - COGS Mult: 0.95× (-5% efficiency gains)
   - Volume Adj: +1% additional growth
   
3. **Worst Case**: Conservative assumptions
   - Revenue Mult: 0.85× (-15%)
   - COGS Mult: 1.10× (+10% cost inflation)
   - Volume Adj: -1% contraction

### How It Works
"In Excel, there's a dropdown in the Inputs sheet. Change it from 'Base' to 'Best', and every formula recalculates using INDEX/MATCH to pull the new multipliers. Revenue increases 15%, margins improve, cash flow improves."

### Business Value
"This lets executives ask: 'What if we lose that big customer?' → Switch to Worst case → See cash runway drop from 18 months to 9 months → Make hiring/spending decisions accordingly."

---

## 5. SENSITIVITY INSIGHTS

### What I Analyzed
Created a 5×5 matrix showing impact of:
- **Price changes**: -10% to +10%
- **Volume changes**: -10% to +10%

### Key Insights
"Example findings:
- **10% price increase** → +$540K annual revenue (no volume change)
- **10% volume increase** → +$600K annual revenue (scales with base)
- **Combined (5% price + 5% volume)** → +$570K (non-linear interaction)

This tells management: 'Focus on volume growth—it has higher leverage than pricing.'"

### Additional Levers Tested
- **COGS % change**: -5% to +5% (supplier negotiations)
- **Hiring rate**: -50% to +50% (headcount planning)
- **CapEx**: -20% to +20% (investment scenarios)

---

## 6. TECHNICAL DECISIONS

### Why No Machine Learning?
"I deliberately avoided ML because:
1. **Auditability**: CFOs need to explain numbers to boards
2. **Reproducibility**: Same inputs must give same outputs
3. **Transparency**: Business users can see the logic
4. **Control**: Analysts can override assumptions

ML is great for pattern recognition, but FP&A is about business logic."

### Why Excel + Python?
"**Excel** is the universal language of finance—every analyst knows it, and executives trust it.

**Python** automates the heavy lifting:
- Generates 36 months of forecasts in seconds
- Writes Excel formulas (not just values)
- Runs 13 automated tests
- Ensures consistency

Best of both worlds: automation + accessibility."

### Formula-Driven vs Value-Only
"Many 'models' are just CSV dumps—values pasted into Excel. Mine writes actual formulas:
```excel
=BaseRevenue * (1+VolGrowth)^t * Seasonality
```
This means:
- **Auditable**: Click any cell, see the logic
- **Flexible**: Change an assumption, everything updates
- **Trustworthy**: No hidden calculations"

---

## 7. RESULTS & IMPACT

### Deliverables
1. **Excel Model**: 7 sheets, 100% formula-driven
2. **Python Engine**: Deterministic forecast generator
3. **Test Suite**: 13 automated validation checks
4. **Documentation**: Model map, talking points, CV bullets

### Validation
- ✅ All 13 tests pass
- ✅ Cash flow reconciles to the penny
- ✅ Scenario switcher works (verified)
- ✅ Depreciation waterfall accurate
- ✅ Working capital logic correct

### Business Value
"This model enables:
- **Scenario planning**: Board presentations with Base/Best/Worst
- **Sensitivity analysis**: 'What if' questions answered instantly
- **Cash runway**: Know when you'll run out of money
- **Hiring decisions**: See payroll impact on cash flow
- **CapEx planning**: Understand depreciation tax shield"

---

## 8. INTERVIEW TALKING POINTS

### For FP&A Roles
"I built this to demonstrate I understand:
- **Driver-based forecasting**: Not just extrapolating trends
- **Three-statement modeling**: P&L, Cash Flow, Balance Sheet
- **Scenario analysis**: Base/Best/Worst case planning
- **Working capital**: DSO/DSI/DPO impact on cash
- **Excel expertise**: Named ranges, INDEX/MATCH, data validation"

### For Data Analyst Roles
"This shows I can:
- **Automate workflows**: Python generates Excel formulas
- **Test rigorously**: 13 automated checks
- **Document thoroughly**: Model map, README, talking points
- **Think like a business**: Not just code, but business logic"

### For Technical Roles
"Technical highlights:
- **xlsxwriter**: Programmatically write Excel formulas
- **Deterministic engine**: No randomness, fully reproducible
- **Test-driven**: pytest suite with 13 checks
- **Modular design**: Separate forecast/export/validation modules"

---

## 9. COMMON QUESTIONS & ANSWERS

### Q: "Why not use Power BI for everything?"
**A**: "Power BI is great for dashboards, but Excel is the standard for financial models. CFOs want to see formulas, not just visuals. I use both: Excel for the model, Power BI for executive dashboards."

### Q: "How long does it take to run?"
**A**: "The Python engine generates 36 months of forecasts in under 2 seconds. Building the Excel file takes about 5 seconds. Total end-to-end: ~10 seconds."

### Q: "Can you add more scenarios?"
**A**: "Yes—just add a row to the Scenario_Table sheet and update the dropdown validation. The formulas automatically pick it up via INDEX/MATCH."

### Q: "How do you handle errors?"
**A**: "I have a Checks sheet with validation formulas:
- Cash must be positive
- Revenue must be positive
- Margins must be < 100%
- No formula errors in Engine sheet

Plus 13 Python unit tests that run automatically."

### Q: "What if assumptions change?"
**A**: "That's the beauty of a formula-driven model. Change any input in the Inputs sheet, and everything recalculates instantly. No need to rebuild."

---

## 10. DEMO SCRIPT (2 Minutes)

### Minute 1: Show the Model
1. Open Excel → Inputs sheet
2. "Here are all our assumptions—revenue growth, costs, headcount"
3. "This dropdown switches scenarios"
4. Change Base → Best
5. Navigate to Engine sheet
6. "Watch revenue increase 15%"

### Minute 2: Show the Code
1. Open terminal
2. `python -m pytest tests/test_sanity.py -v`
3. "13 automated tests—all passing"
4. `python src/forecast_engine.py`
5. "Generates 36 months in 2 seconds"
6. "Every number is auditable, deterministic, and reproducible"

---

## Key Takeaway

**"I built a corporate-grade FP&A model that combines the automation of Python with the transparency of Excel. It's deterministic (not ML), auditable (formulas, not values), and dynamic (scenario switching). This demonstrates I can bridge technical skills with business needs—which is exactly what modern FP&A roles require."**
