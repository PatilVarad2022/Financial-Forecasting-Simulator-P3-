# P3 FP&A Model - Sheet-by-Sheet Documentation

## Overview
This document provides a comprehensive guide to each sheet in the `FPnA_Model_with_formulas.xlsx` workbook.

---

## 1. Inputs Sheet

### Purpose
Central repository for all model assumptions and drivers. All calculations reference this sheet.

### Key Sections

#### A. Scenario Control
- **Active Scenario** (B5): Dropdown selector (Base/Best/Worst)
- **Named Range**: `ScenarioSelector`

#### B. Revenue Drivers
- **Base Monthly Revenue**: Starting revenue per month
- **Volume Growth**: Monthly volume growth rate
- **Price Growth**: Monthly price inflation rate
- **Seasonality**: 12-month array (Jan-Dec multipliers)

#### C. Cost Drivers
- **COGS %**: Cost of goods sold as % of revenue
- **Fixed OpEx**: Monthly fixed operating expenses
- **OpEx Variable %**: Variable opex as % of revenue
- **Tax Rate**: Corporate tax rate

#### D. Headcount Drivers
- **Start Headcount**: Initial employee count
- **Hiring Rate**: Monthly hiring rate
- **Avg Salary**: Average monthly salary per employee

#### E. Working Capital Drivers
- **DSO**: Days Sales Outstanding (AR calculation)
- **DSI**: Days Sales Inventory
- **DPO**: Days Payable Outstanding

#### F. Assets & Funding
- **Useful Life**: Depreciation period in months
- **Initial Cash**: Opening cash balance

### Named Ranges
All inputs are defined as named ranges for easy formula referencing:
- `BaseRevenue`, `VolGrowth`, `PriceGrowth`
- `COGS_Pct`, `FixedOpEx`, `OpExVarPct`
- `HC_Start`, `HiringRate`, `AvgSalary`
- `DSO`, `DSI`, `DPO`
- `UsefulLife`, `InitCash`, `TaxRate`

---

## 2. Scenario_Table Sheet

### Purpose
Defines multipliers for Base/Best/Worst case scenarios.

### Structure
| Scenario | Revenue_Mult | COGS_Mult | Vol_Adj | Price_Adj | CapEx_Mult |
|----------|--------------|-----------|---------|-----------|------------|
| Base     | 1.00         | 1.00      | 0.00    | 0.00      | 1.00       |
| Best     | 1.15         | 0.95      | 0.01    | 0.005     | 1.20       |
| Worst    | 0.85         | 1.10      | -0.01   | -0.005    | 0.80       |

### Usage
Engine formulas use INDEX/MATCH to pull multipliers based on `ScenarioSelector`.

---

## 3. Engine Sheet

### Purpose
Core calculation engine with monthly P&L projections.

### Row Structure
1. **Month Index**: Sequential month counter
2. **Revenue**: `=BaseRevenue * (1+VolGrowth+VolAdj)^t * (1+PriceGrowth+PriceAdj)^t * Seasonality * RevMult`
3. **COGS**: `=Revenue * COGS_Pct * COGSMult`
4. **OpEx**: `=FixedOpEx + (Revenue * OpExVarPct) + Payroll`
5. **Payroll**: `=Headcount * AvgSalary`
6. **Headcount**: `=HC_Start + INT(HiringRate * t)`
7. **EBITDA**: `=Revenue - COGS - OpEx`
8. **CapEx**: Base schedule × CapExMult
9. **Depreciation**: Linked from Depreciation_Sched
10. **EBIT**: `=EBITDA - Depreciation`
11. **Tax**: `=MAX(0, EBIT * TaxRate)`
12. **Net Income**: `=EBIT - Tax`

### Key Features
- All formulas (no hardcoded values)
- Scenario-aware (INDEX/MATCH lookups)
- Month-over-month calculations

---

## 4. Depreciation_Sched Sheet

### Purpose
Tracks depreciation waterfall for each CapEx batch.

### Structure
- **Row 1**: Dates (monthly headers)
- **Row 2**: New CapEx (linked from Engine)
- **Rows 3+**: Depreciation batches (one per CapEx event)
- **Bottom Row**: Total Depreciation (sum of all active batches)

### Formula Logic
For each batch:
```excel
=IF(AND(CurrentMonth >= BatchMonth, CurrentMonth < BatchMonth + UsefulLife), 
    BatchCapEx / UsefulLife, 
    0)
```

### Named Range
`DeprStream`: Total depreciation row used by Engine sheet

---

## 5. Working_Capital Sheet

### Purpose
Calculates working capital components and cash flow statement.

### Columns
1. **Date**: Month identifier
2. **Revenue**: Linked from Engine
3. **COGS**: Linked from Engine
4. **OpEx**: Linked from Engine
5. **AR**: `=Revenue / 365 * DSO`
6. **Inventory**: `=COGS / 365 * DSI`
7. **AP**: `=COGS / 365 * DPO`
8. **Net WC**: `=AR + Inventory - AP`
9. **Delta WC**: `=Current_WC - Prior_WC`
10. **Net Income**: Linked from Engine
11. **Depreciation**: Linked from Engine
12. **CapEx**: Linked from Engine
13. **Cash Flow**: `=NI + Depr - DeltaWC - CapEx`
14. **Cash Balance**: `=Prior_Cash + Cash_Flow`

### Key Formulas
- **Operating CF**: Net Income + Depreciation - ΔWC
- **Investing CF**: -CapEx
- **Cash Roll-forward**: Cumulative sum

---

## 6. Sensitivity Sheet

### Purpose
Analyzes impact of key lever changes on financial metrics.

### Structure
**2-Way Data Table**: Price × Volume

|           | Vol-10% | Vol-5% | Vol0% | Vol+5% | Vol+10% |
|-----------|---------|--------|-------|--------|---------|
| Price-10% | Formula | ...    | ...   | ...    | ...     |
| Price-5%  | Formula | ...    | ...   | ...    | ...     |
| Price 0%  | Formula | ...    | ...   | ...    | ...     |
| Price+5%  | Formula | ...    | ...   | ...    | ...     |
| Price+10% | Formula | ...    | ...   | ...    | ...     |

### Formula
```excel
=SUM(Engine!Revenue) * (1 + PriceShift) * (1 + VolumeShift)
```

### Outputs
- Total Revenue impact
- EBITDA impact (can be added)
- Cash runway impact (can be added)

---

## 7. Checks Sheet

### Purpose
Automated validation and audit checks.

### Validation Rules
1. **Cash Positive**: `=MIN(Working_Capital!CashBalance) > 0`
2. **Revenue Positive**: `=SUM(Engine!Revenue) > 0`
3. **Balance Sheet**: Placeholder for Assets = Liab + Equity
4. **No Errors**: Checks for formula errors in Engine

### Usage
All checks should return TRUE or positive values. Any FALSE indicates model issue.

---

## Dependency Flow

```
Inputs (Drivers)
    ↓
Scenario_Table (Multipliers)
    ↓
Engine (Monthly P&L)
    ↓ ↓ ↓
    ↓ ↓ Working_Capital (Cash Flow)
    ↓ ↓
    ↓ Depreciation_Sched (Waterfall)
    ↓
Sensitivity (What-If Analysis)
    ↓
Checks (Validation)
```

---

## Formula Reference Guide

### Revenue Calculation
```excel
=BaseRevenue 
* ((1 + VolGrowth + INDEX(Scenario_Table, MATCH(ScenarioSelector, ...), 4))^t)
* ((1 + PriceGrowth + INDEX(Scenario_Table, MATCH(ScenarioSelector, ...), 5))^t)
* INDEX(Seasonality, MONTH(Date))
* INDEX(Scenario_Table, MATCH(ScenarioSelector, ...), 2)
```

### COGS Calculation
```excel
=Revenue * COGS_Pct * INDEX(Scenario_Table, MATCH(ScenarioSelector, ...), 3)
```

### Working Capital
```excel
AR = Revenue / 365 * DSO
Inventory = COGS / 365 * DSI
AP = COGS / 365 * DPO
Net WC = AR + Inventory - AP
```

### Cash Flow
```excel
Operating CF = Net Income + Depreciation - Delta_WC
Investing CF = -CapEx
Cash Balance = Prior_Cash + Operating_CF + Investing_CF
```

---

## How to Use This Model

### 1. Change Assumptions
- Navigate to **Inputs** sheet
- Modify any driver value
- All sheets recalculate automatically

### 2. Switch Scenarios
- Go to **Inputs** sheet
- Change **Active Scenario** dropdown
- Watch **Engine** and **Working_Capital** update

### 3. Run Sensitivity
- Open **Sensitivity** sheet
- Review Price × Volume matrix
- Add additional levers as needed

### 4. Validate Model
- Check **Checks** sheet
- All validations should pass (TRUE)
- Investigate any FALSE results

---

## Maintenance Notes

### Adding New Months
1. Insert column in Engine sheet
2. Copy formulas from previous month
3. Update date reference
4. Depreciation and WC sheets auto-extend

### Adding New Scenarios
1. Add row to Scenario_Table
2. Define multipliers
3. Add to ScenarioSelector validation list

### Adding New Drivers
1. Add to Inputs sheet
2. Define named range
3. Reference in Engine formulas

---

## Version History
- **v1.0** (2025-12-10): Initial formula-based model
- Deterministic engine
- Scenario switching
- Sensitivity analysis
- Full cash flow reconciliation
