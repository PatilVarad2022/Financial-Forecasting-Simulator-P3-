import json
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os

def load_json(path):
    with open(path,'r') as f:
        return json.load(f)

def make_month_list(start, months):
    return [(start + relativedelta(months=i)).strftime('%Y-%m-01') for i in range(months)]

def driver_forecast(start_date_str='2025-01-01', months_horizon=36, opening_cash=500000.0):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    drivers_path = os.path.join(base_dir, 'data', 'config', 'drivers.json')
    scenarios_path = os.path.join(base_dir, 'data', 'config', 'scenarios.json')
    output_path = os.path.join(base_dir, 'data', 'processed', 'forecast_output.csv')
    
    drivers = load_json(drivers_path)
    scenarios = load_json(scenarios_path) if os.path.exists(scenarios_path) else {}
    capex_sched = drivers.get('capex_schedule', {})  # dict of 'YYYY-MM' -> amount
    useful_life_months = drivers.get('useful_life_months', 60)
    dep_table = {}  # month -> depreciation amount (simple straight-line per capex item is assumed aggregated)
    start_date = datetime.fromisoformat(start_date_str)
    months = months_horizon
    rows = []
    cash = drivers.get('initial_cash_balance', opening_cash)
    prev_wc = 0.0

    for m in range(months):
        date = start_date + relativedelta(months=m)
        ym = date.strftime('%Y-%m')
        month_idx = date.month - 1
        seasonality = drivers.get('seasonality', [1]*12)[month_idx]
        months_from_start = m
        base_rev = drivers.get('base_revenue_monthly', 0.0)
        vol_growth = drivers.get('volume_growth_monthly', 0.0)
        price_growth = drivers.get('price_growth_monthly', 0.0)
        revenue = base_rev * ((1+vol_growth)**months_from_start) * ((1+price_growth)**months_from_start) * seasonality

        cogs_pct = drivers.get('cogs_pct', 0.0)
        cogs = revenue * cogs_pct

        fixed_opex = drivers.get('fixed_opex_monthly', 0.0)
        opex_var_pct = drivers.get('opex_var_pct', 0.0)
        opex = fixed_opex + revenue * opex_var_pct

        headcount = drivers.get('headcount_start', 0) + int(drivers.get('hiring_rate_monthly', 0)*months_from_start)
        avg_salary = drivers.get('avg_salary_monthly', 0.0)
        payroll = headcount * avg_salary

        capex = capex_sched.get(ym, 0.0)
        # add capex to depreciation schedule: simple approach -> add monthly dep for next useful_life_months
        if capex != 0:
            monthly_dep = capex / float(useful_life_months)
            for j in range(useful_life_months):
                dep_month = (date + relativedelta(months=j)).strftime('%Y-%m')
                dep_table[dep_month] = dep_table.get(dep_month, 0.0) + monthly_dep

        depreciation = dep_table.get(ym, drivers.get('depreciation_monthly', 0.0))

        tax_pct = drivers.get('tax_rate', 0.0)
        ebitda = revenue - cogs - opex - payroll
        ebt = ebitda - depreciation
        tax = max(0.0, ebt * tax_pct)
        net_income = ebt - tax

        # Working capital
        dso = drivers.get('dso', 30.0)
        dsi = drivers.get('dsi', 30.0)
        dpo = drivers.get('dpo', 30.0)
        ar = revenue / 30.0 * dso # Simplification for monthly
        inventory = cogs / 30.0 * dsi
        ap = cogs / 30.0 * dpo
        wc = ar + inventory - ap
        delta_wc = wc - prev_wc

        operating_cf = net_income + depreciation - delta_wc
        investing_cf = -capex
        financing_cf = 0.0  # keep simple; extend later if debt/equity flows exist
        cash = cash + operating_cf + investing_cf + financing_cf

        rows.append({
            'date': date.strftime('%Y-%m-01'),
            'revenue': revenue,
            'cogs': cogs,
            'opex': opex,
            'payroll': payroll,
            'headcount': headcount,
            'capex': capex,
            'depreciation': depreciation,
            'ebitda': ebitda,
            'ebt': ebt,
            'tax': tax,
            'net_income': net_income,
            'ar': ar,
            'inventory': inventory,
            'ap': ap,
            'wc': wc,
            'delta_wc': delta_wc,
            'operating_cf': operating_cf,
            'investing_cf': investing_cf,
            'financing_cf': financing_cf,
            'cash_balance': cash # Renamed to standard
        })

        prev_wc = wc

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Forecast saved to {output_path}")
    return df

if __name__ == '__main__':
    driver_forecast(start_date_str='2025-01-01', months_horizon=36)
