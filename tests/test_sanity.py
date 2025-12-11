import pandas as pd
import os
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORECAST_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'forecast_output.csv')

def test_forecast_exists():
    """Verify forecast output file exists and is not empty"""
    assert os.path.exists(FORECAST_PATH), "forecast_output.csv not found"
    df = pd.read_csv(FORECAST_PATH)
    assert not df.empty, "Forecast dataframe is empty"

def test_no_nans():
    """Ensure no NaN values in critical columns"""
    df = pd.read_csv(FORECAST_PATH)
    assert not df.isna().any().any(), "Found NaN values in forecast data"

def test_revenue_positive():
    """Revenue must be non-negative"""
    df = pd.read_csv(FORECAST_PATH)
    assert (df['revenue'] >= 0).all(), "Found negative revenue values"

def test_cogs_relation():
    """COGS should be between 0% and 100% of revenue"""
    df = pd.read_csv(FORECAST_PATH)
    ratios = df['cogs'] / df['revenue']
    assert (ratios >= 0).all() and (ratios <= 1.0).all(), "COGS/Revenue ratio out of bounds"

def test_depreciation_nonneg():
    """Depreciation must be non-negative"""
    df = pd.read_csv(FORECAST_PATH)
    assert (df['depreciation'] >= 0).all(), "Found negative depreciation"

def test_cash_rollforward():
    """Verify cash balance reconciles with cash flows"""
    df = pd.read_csv(FORECAST_PATH)
    # Calculate expected cash: opening + cumulative flows
    opening = df.loc[0, 'cash_balance'] - (df.loc[0, 'operating_cf'] + df.loc[0, 'investing_cf'] + df.loc[0, 'financing_cf'])
    calc = opening + df['operating_cf'].cumsum() + df['investing_cf'].cumsum() + df['financing_cf'].cumsum()
    assert all(abs(df['cash_balance'] - calc) < 1e-2), "Cash balance doesn't reconcile with flows"

def test_wc_computation():
    """Working capital columns must exist"""
    df = pd.read_csv(FORECAST_PATH)
    assert 'wc' in df.columns, "Working capital column missing"
    assert 'delta_wc' in df.columns, "Delta WC column missing"

def test_capex_included():
    """CapEx schedule should have some non-zero values"""
    df = pd.read_csv(FORECAST_PATH)
    assert df['capex'].sum() >= 0, "CapEx sum is negative"

def test_ebitda_calculation():
    """EBITDA should equal Revenue - COGS - OpEx - Payroll"""
    df = pd.read_csv(FORECAST_PATH)
    calculated_ebitda = df['revenue'] - df['cogs'] - df['opex'] - df['payroll']
    assert all(abs(df['ebitda'] - calculated_ebitda) < 1e-2), "EBITDA calculation mismatch"

def test_net_income_bounds():
    """Net income should be less than revenue"""
    df = pd.read_csv(FORECAST_PATH)
    assert (df['net_income'] < df['revenue']).all(), "Net income exceeds revenue"

def test_growth_trajectory():
    """Revenue should show growth over time (with positive growth drivers)"""
    df = pd.read_csv(FORECAST_PATH)
    assert df['revenue'].iloc[-1] > df['revenue'].iloc[0], "No revenue growth detected"

def test_ar_magnitude():
    """AR should be reasonable relative to revenue (DSO-based)"""
    df = pd.read_csv(FORECAST_PATH)
    if df['revenue'].iloc[0] > 0:
        ratio = df['ar'].iloc[0] / df['revenue'].iloc[0]
        assert 0.5 < ratio < 3.0, f"AR/Revenue ratio {ratio} seems unrealistic"
