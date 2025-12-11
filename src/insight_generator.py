import pandas as pd
import numpy as np
import os

class InsightGenerator:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        self.df = pd.read_csv(data_path)
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df.sort_values('Date', inplace=True)
        elif 'Month' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Month'])
            self.df.sort_values('Date', inplace=True)

    def generate_variance_commentary(self, latest_month_idx=-1):
        latest = self.df.iloc[latest_month_idx]
        prev = self.df.iloc[latest_month_idx - 1]
        
        comments = []
        metrics = ['Revenue', 'EBITDA']
        
        for m in metrics:
            if m in self.df.columns:
                val_curr = latest[m]
                val_prev = prev[m]
                growth = (val_curr - val_prev) / val_prev * 100
                direction = "up" if growth > 0 else "down"
                comments.append(f"- {m} {direction} {abs(growth):.1f}% MoM.")
                
        # Margin
        if 'Revenue' in self.df.columns and 'EBITDA' in self.df.columns:
            margin_curr = latest['EBITDA'] / latest['Revenue'] * 100
            margin_prev = prev['EBITDA'] / prev['Revenue'] * 100
            bps = (margin_curr - margin_prev) * 100
            direction = "expanded" if bps > 0 else "compressed"
            comments.append(f"- EBITDA margin {direction} {abs(bps):.0f}bps.")
            
        return comments

    def generate_trend_detection(self):
        # Rolling correlation or slope
        comments = []
        
        # Check Cost vs Revenue Growth (Last 6 months)
        if len(self.df) > 6:
            recent = self.df.tail(6)
            rev_growth = recent['Revenue'].pct_change().mean()
            if 'COGS' in recent.columns and 'OpEx_Sales' in recent.columns:
                cost_series = recent['COGS'] + recent['OpEx_Sales'] + recent['OpEx_Admin'] if 'OpEx_Admin' in recent.columns else 0
                cost_growth = cost_series.pct_change().mean()
                
                if cost_growth > rev_growth:
                    comments.append(f"⚠️ Trend Alert: Cost growth ({cost_growth*100:.1f}%) exceeding revenue growth ({rev_growth*100:.1f}%) in last 6 months.")
        
        # Seasonality (Simple Peak detection)
        # Find month with highest average revenue
        self.df['MonthNum'] = self.df['Date'].dt.month
        monthly_avg = self.df.groupby('MonthNum')['Revenue'].mean()
        peak_month = monthly_avg.idxmax()
        import calendar
        month_name = calendar.month_name[peak_month]
        comments.append(f"ℹ️ Seasonality: {month_name} is historically the strongest month.")
        
        return comments

    def check_risks(self):
        comments = []
        # Cash Runway
        # Assuming we have a 'Cash_Balance' or we just check CashFlow
        # If CashFlow is consistently negative
        if 'CashFlow' in self.df.columns:
            recent_cf = self.df['CashFlow'].tail(3)
            if (recent_cf < 0).all():
                comments.append("🚩 Risk Alert: Negative Cash Flow for last 3 months.")
                
            # Runway (Proxy: if we had a Balance column, we'd divide. Here we just warn)
        
        return comments

    def generate_report(self):
        print("🧠 Generating Insights Report...")
        
        report_sections = []
        
        report_sections.append("FP&A AUTOMATED INSIGHTS REPORT")
        report_sections.append("==============================")
        report_sections.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
        report_sections.append("")
        
        # 1. Commentary
        report_sections.append("1. MONTHLY VARIANCE COMMENTARY")
        report_sections.extend(self.generate_variance_commentary())
        report_sections.append("")
        
        # 2. Trends
        report_sections.append("2. TREND DETECTION")
        report_sections.extend(self.generate_trend_detection())
        report_sections.append("")
        
        # 3. Risks
        report_sections.append("3. RISK ALERTS")
        report_sections.extend(self.check_risks())
        report_sections.append("")
        
        # Save
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_sections))
            
        print(f"📝 Insights Report saved: {self.output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    # Use scenario output or forecast output
    input_path = os.path.join(base_dir, 'data', 'processed', 'scenario_output.csv')
    
    # If scenario output doesn't exist yet, fallback (for dev testing)
    if not os.path.exists(input_path):
        input_path = os.path.join(base_dir, 'data', 'processed', 'forecast_output.csv')

    output_path = os.path.join(base_dir, 'outputs', 'insights_report.txt')
    
    # Needs to handle the scenario file format (wide or long)
    # If 'scenario_output.csv' is long (Date, Scenario, ...), we should probably pick 'Base' scenario for insights
    
    df = pd.read_csv(input_path)
    if 'Scenario' in df.columns:
        df = df[df['Scenario'] == 'Base']
        
    # Save temp for class usage to avoid re-reading complexities in __main__
    temp_path = input_path.replace('.csv', '_temp_base.csv')
    df.to_csv(temp_path, index=False)
    
    generator = InsightGenerator(temp_path, output_path)
    generator.generate_report()
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
