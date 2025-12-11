import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

class FinancialDataGenerator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.start_date = datetime.strptime(self.config["start_date"], "%Y-%m-%d")
        self.years = 5
        self.months = self.years * 12
        
    def generate_date_range(self):
        # Generate 1st of month dates
        return [self.start_date + timedelta(days=32*i).replace(day=1) for i in range(self.months)]

    def generate_financials(self):
        dates = pd.date_range(start=self.start_date, periods=self.months, freq='MS')
        
        # Base trends
        t = np.linspace(0, self.months, self.months)
        
        # Revenue Generation
        # Base * (1 + Growth)^t * Seasonality * Noise
        growth_monthly = (1 + self.config["volume_growth_rate"]) ** (1/12) - 1
        trend_factor = (1 + growth_monthly) ** t
        
        seasonality = np.array(self.config["seasonality_factors"] * self.years)
        
        # Add some random noise (volatility)
        noise = np.random.normal(1, 0.05, self.months)
        
        revenue = self.config["base_revenue"] * trend_factor * seasonality * noise
        
        # COGS Generation (Assume ~40-50% margin + inflation impact)
        # Cost inflation makes margin easier to hit over time if prices don't keep up
        # But we assume price_increase simulates revenue keeping up, so we'll link COGS to Revenue roughly
        cogs_ratio = 0.55  # Base COGS ratio
        cogs = revenue * cogs_ratio * np.random.normal(1, 0.02, self.months)
        
        # OpEx Generation
        # Sales driven OpEx (Marketing, distribute)
        opex_sales = revenue * 0.15 * np.random.normal(1, 0.05, self.months)
        
        # Admin OpEx (Fixed + Salary Inflation)
        base_admin = 150000
        salary_inflation_monthly = (1 + self.config["salary_inflation"]) ** (1/12) - 1
        admin_trend = (1 + salary_inflation_monthly) ** t
        opex_admin = base_admin * admin_trend * np.random.normal(1, 0.01, self.months)
        
        # Capex (Lumpy - large spend in Q1/Q3 typically or random)
        capex = np.zeros(self.months)
        # Randomly assign capex events (approx 2 per year)
        capex_events = np.random.choice(range(self.months), self.years * 2, replace=False)
        capex[capex_events] = self.config["capex_plan"] / 2 * np.random.uniform(0.8, 1.2, len(capex_events))
        
        # Cash Flow Proxy (Simple: EBITDA - Capex +/- Working Capital changes)
        # Simplified: Revenue (In) - Expenses (Out) with some lag
        # Cash In = 80% Revenue (Month 0) + 20% Revenue (Month -1)
        revenue_lag = np.roll(revenue, 1)
        revenue_lag[0] = revenue[0] # Handle first month
        cash_in = 0.8 * revenue + 0.2 * revenue_lag
        
        cash_out = cogs + opex_sales + opex_admin + capex
        
        # Create DataFrame
        df = pd.DataFrame({
            'Month': dates,
            'Revenue': revenue,
            'COGS': cogs,
            'OpEx_Sales': opex_sales,
            'OpEx_Admin': opex_admin,
            'Capex': capex,
            'Cash_In': cash_in,
            'Cash_Out': cash_out
        })
        
        # Rounding for clean CSV
        cols = ['Revenue', 'COGS', 'OpEx_Sales', 'OpEx_Admin', 'Capex', 'Cash_In', 'Cash_Out']
        df[cols] = df[cols].round(2)
        
        return df

    def generate_dim_date(self, output_path):
        print("📅 Generating DimDate...")
        # Range: Start Date -> 5 Years History + 2 Years Forecast Buffer
        total_months = self.months + 24
        dates = pd.date_range(start=self.start_date, periods=total_months, freq='MS')
        
        dim_date = pd.DataFrame({
            'Date': dates,
            'Year': dates.year,
            'Quarter': dates.quarter,
            'MonthNum': dates.month,
            'MonthName': dates.strftime('%B'),
            'IsForecast': [True if i >= self.months else False for i in range(total_months)]
        })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dim_date.to_csv(output_path, index=False)
        print(f"✅ DimDate saved: {output_path}")

    def save_data(self, df, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Data generated successfully: {output_path}")
        print(df.head())

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config', 'drivers.json')
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw', 'historical_financials.csv')
    dim_date_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'dim_date.csv')
    
    gen = FinancialDataGenerator(config_path)
    df = gen.generate_financials()
    gen.save_data(df, output_path)
    gen.generate_dim_date(dim_date_path)
