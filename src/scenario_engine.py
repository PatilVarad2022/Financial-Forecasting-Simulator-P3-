import pandas as pd
import numpy as np
import os
import json

class ScenarioEngine:
    def __init__(self, forecast_path):
        self.forecast_path = forecast_path
        self.df = pd.read_csv(forecast_path)
        
    def generate_scenarios(self):
        print("⚡ Generating Scenarios...")
        
        # Load Scenarios from JSON
        config_path = os.path.join(os.path.dirname(os.path.dirname(self.forecast_path)), 'config', 'scenarios.json')
        with open(config_path, 'r') as f:
            scenarios_config = json.load(f)
            
        all_scenarios = []
        
        for name, params in scenarios_config.items():
            temp_df = self.df.copy()
            temp_df['Scenario'] = name
            
            # Apply multipliers
            rev_mult = params.get('revenue_multiplier', 1.0)
            cost_mult = params.get('cost_multiplier', 1.0)
            
            temp_df['Revenue_Forecast'] *= rev_mult
            
            # Apply cost multiplier to COGS and OpEx
            temp_df['COGS_Forecast'] *= cost_mult
            temp_df['OpEx_Sales_Forecast'] *= cost_mult
            temp_df['OpEx_Admin_Forecast'] *= cost_mult
            temp_df['Capex_Forecast'] *= cost_mult # Assuming Capex scales with cost scenarios
            
            # Recalculate EBITDA
            temp_df['EBITDA_Forecast'] = (
                temp_df['Revenue_Forecast'] 
                - temp_df['COGS_Forecast'] 
                - temp_df['OpEx_Sales_Forecast'] 
                - temp_df['OpEx_Admin_Forecast']
            )
            
            # Recalculate Cash Flow (Proxy)
            if 'Cash_In_Forecast' in temp_df.columns:
                 # Adjust Cash In/Out roughly by multiplier logic
                 temp_df['Cash_In_Forecast'] *= rev_mult
                 temp_df['Cash_Out_Forecast'] *= cost_mult
                 temp_df['CashFlow_Forecast'] = temp_df['Cash_In_Forecast'] - temp_df['Cash_Out_Forecast']
            else:
                 temp_df['CashFlow_Forecast'] = temp_df['EBITDA_Forecast'] # Fallback
            
            all_scenarios.append(temp_df)
            
        final_df = pd.concat(all_scenarios, ignore_index=True)
        print(f"✅ Generated Scenarios: {len(final_df)} rows")
        return final_df

    def run_sensitivity_analysis(self):
        print("〰️ Running Sensitivity Analysis...")
        config_path = os.path.join(os.path.dirname(os.path.dirname(self.forecast_path)), 'config', 'sensitivity.json')
        if not os.path.exists(config_path):
            print("No sensitivity config found.")
            return None

        with open(config_path, 'r') as f:
            sens_config = json.load(f)
            
        # Base case
        base_df = self.df.copy()
        base_annual_rev = base_df['Revenue_Forecast'].sum()
        base_annual_ebitda = base_df['EBITDA_Forecast'].sum()
        
        results = []
        
        # Pricing Change (= Revenue Change)
        for change in sens_config.get('pricing_change', []):
            impact = 1 + change
            rev = base_annual_rev * impact
            # EBITDA changes by revenue delta (assuming costs fixed for pricing change logic, strictly margin expansion)
            # Revenue_New - Costs_Base
            costs = base_df['COGS_Forecast'].sum() + base_df['OpEx_Sales_Forecast'].sum() + base_df['OpEx_Admin_Forecast'].sum()
            ebitda = rev - costs
            results.append({'Dimension': 'Pricing', 'Change': change, 'Annual_Revenue': rev, 'Annual_EBITDA': ebitda})

        # OpEx Change
        for change in sens_config.get('opex_change', []):
            impact = 1 + change
            # Costs change
            costs = (base_df['OpEx_Sales_Forecast'].sum() + base_df['OpEx_Admin_Forecast'].sum()) * impact + base_df['COGS_Forecast'].sum()
            ebitda = base_annual_rev - costs
            results.append({'Dimension': 'OpEx', 'Change': change, 'Annual_Revenue': base_annual_rev, 'Annual_EBITDA': ebitda})
            
        return pd.DataFrame(results)

    def save_outputs(self, scenario_df, sensitivity_df, output_dir):
        # 1. Save Full Scenario Output
        # Clean columns to remove _Forecast suffix for cleaner final table
        clean_df = scenario_df.copy()
        clean_df.columns = [c.replace('_Forecast', '') for c in clean_df.columns]
        
        # Select required columns: Date, Scenario, Revenue, COGS, EBITDA, CashFlow
        # Map Month to Date
        if 'Month' in clean_df.columns:
            clean_df.rename(columns={'Month': 'Date'}, inplace=True)
        
        # Ensure CashFlow exists
        if 'CashFlow' not in clean_df.columns:
             clean_df['CashFlow'] = clean_df['EBITDA'] # fallback
             
        # Add all necessary columns for Excel Model
        cols = ['Date', 'Scenario', 'Revenue', 'COGS', 'EBITDA', 'CashFlow', 
                'OpEx_Sales', 'OpEx_Admin', 'Capex', 'Cash_In', 'Cash_Out']
        final_cols = [c for c in cols if c in clean_df.columns]
        
        scen_path = os.path.join(output_dir, 'scenario_output.csv')
        clean_df[final_cols].to_csv(scen_path, index=False)
        print(f"💾 Scenario Output saved: {scen_path}")
        
        # 2. Save Sensitivity
        if sensitivity_df is not None:
            sens_path = os.path.join(output_dir, 'sensitivity_output.csv')
            sensitivity_df.to_csv(sens_path, index=False)
            print(f"💾 Sensitivity Output saved: {sens_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(base_dir, 'data', 'processed', 'forecast_output.csv')
    output_dir = os.path.join(base_dir, 'data', 'processed')
    
    engine = ScenarioEngine(input_path)
    scenarios = engine.generate_scenarios()
    sens_df = engine.run_sensitivity_analysis()
    engine.save_outputs(scenarios, sens_df, output_dir)
