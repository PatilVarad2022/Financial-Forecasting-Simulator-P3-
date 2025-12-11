import pandas as pd
import os
import xlsxwriter
import json
from datetime import datetime

class ExportModule:
    def __init__(self, history_path, forecast_path):
        self.history_path = history_path
        self.forecast_path = forecast_path
        # Load forecast data to get dates and baseline values for validation
        self.forecast_df = pd.read_csv(forecast_path)
        
    def create_excel_model(self, output_path):
        print(f"📗 Building Corporate Excel Model (Formulas) at {output_path}...")
        
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        workbook = writer.book
        
        # ---------------------------------------------------------
        # Formats
        # ---------------------------------------------------------
        fmt_header = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'border': 1, 'align': 'center'})
        fmt_input = workbook.add_format({'bg_color': '#FFF2CC', 'border': 1}) # Yellowish for inputs
        fmt_calc = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1})
        fmt_num = workbook.add_format({'num_format': '#,##0', 'border': 1})
        fmt_curr = workbook.add_format({'num_format': '$#,##0', 'border': 1})
        fmt_pct = workbook.add_format({'num_format': '0.00%', 'border': 1})
        fmt_month = workbook.add_format({'num_format': 'mmm-yy', 'bold': True, 'align': 'center', 'bg_color': '#ECF0F1', 'border': 1})
        
        # Load Drivers
        base_dir = os.path.dirname(os.path.dirname(self.history_path))
        drivers_path = os.path.join(base_dir, 'config', 'drivers.json')
        with open(drivers_path) as f:
            drivers = json.load(f)

        # ---------------------------------------------------------
        # 1. Inputs Sheet (Categorized)
        # ---------------------------------------------------------
        ws_inp = workbook.add_worksheet('Inputs')
        ws_inp.set_column('A:A', 30)
        ws_inp.set_column('B:B', 15)
        ws_inp.set_column('C:C', 20)
        
        ws_inp.write('A1', 'P3 FP&A Model Inputs', workbook.add_format({'bold': True, 'font_size': 14}))
        
        row = 2
        # Helper to write input block
        def write_block(title, items):
            nonlocal row
            ws_inp.write(row, 0, title, fmt_header)
            ws_inp.write(row, 1, 'Value', fmt_header)
            ws_inp.write(row, 2, 'Named Range', fmt_header)
            row += 1
            for lbl, val, name, fmt in items:
                ws_inp.write(row, 0, lbl, fmt_calc)
                is_input = True
                # Special handling for lists/selectors
                if name == 'ScenarioSelector':
                    ws_inp.data_validation(row, 1, row, 1, {'validate': 'list', 'source': ['Base', 'Best', 'Worst']})
                
                ws_inp.write(row, 1, val, fmt if fmt else fmt_input)
                ws_inp.write(row, 2, name, fmt_calc)
                workbook.define_name(name, f'=Inputs!$B${row+1}')
                row += 1
            row += 1
            
        write_block("SCENARIO CONTROL", [
            ('Active Scenario', 'Base', 'ScenarioSelector', None)
        ])
        
        write_block("REVENUE DRIVERS", [
            ('Base Monthly Revenue', drivers.get('base_revenue_monthly', 150000), 'BaseRevenue', fmt_curr),
            ('Volume Growth (mo)', drivers.get('volume_growth_monthly', 0.02), 'VolGrowth', fmt_pct),
            ('Price Growth (mo)', drivers.get('price_growth_monthly', 0.005), 'PriceGrowth', fmt_pct)
        ])
        
        write_block("COST DRIVERS", [
            ('COGS % of Rev', drivers.get('cogs_pct', 0.40), 'COGS_Pct', fmt_pct),
            ('Fixed OpEx (Monthly)', drivers.get('fixed_opex_monthly', 45000), 'FixedOpEx', fmt_curr),
            ('OpEx Variable %', drivers.get('opex_var_pct', 0.10), 'OpExVarPct', fmt_pct),
            ('Tax Rate', drivers.get('tax_rate', 0.25), 'TaxRate', fmt_pct)
        ])
        
        write_block("HEADCOUNT DRIVERS", [
            ('Start Headcount', drivers.get('headcount_start', 12), 'HC_Start', fmt_num),
            ('Hiring Rate (mo)', drivers.get('hiring_rate_monthly', 0.2), 'HiringRate', fmt_pct),
            ('Avg Salary', drivers.get('avg_salary_monthly', 6000), 'AvgSalary', fmt_curr)
        ])
        
        write_block("WORKING CAPITAL DRIVERS", [
            ('DSO (Days Sales Outstanding)', drivers.get('working_capital', {}).get('dso', 45), 'DSO', fmt_num),
            ('DSI (Days Sales Inventory)', drivers.get('working_capital', {}).get('dsi', 30), 'DSI', fmt_num),
            ('DPO (Days Payable Outstanding)', drivers.get('working_capital', {}).get('dpo', 30), 'DPO', fmt_num)
        ])
        
        write_block("ASSETS & FUNDING", [
            ('Useful Life (Months)', drivers.get('useful_life_months', 60), 'UsefulLife', fmt_num),
            ('Initial Cash', drivers.get('initial_cash_balance', 500000), 'InitCash', fmt_curr)
        ])
        
        # Seasonality Array
        ws_inp.write(row, 0, "SEASONALITY PROFILE", fmt_header)
        seas = drivers.get('seasonality', [1]*12)
        for i, s in enumerate(seas):
            ws_inp.write(row+1, i, i+1, fmt_month) # 1, 2, ...
            ws_inp.write(row+2, i, s, fmt_pct)
        
        # Define range for seasonality
        # Horizontal range: Inputs!A(Row+3):L(Row+3)
        workbook.define_name('Seasonality', f'=Inputs!$A${row+3}:$L${row+3}')
        
        # ---------------------------------------------------------
        # 2. Scenario Data
        # ---------------------------------------------------------
        ws_scen = workbook.add_worksheet('Scenario_Table')
        headers = ['Scenario', 'Revenue_Mult', 'COGS_Mult', 'Vol_Adj', 'Price_Adj', 'CapEx_Mult']
        for c, h in enumerate(headers):
            ws_scen.write(0, c, h, fmt_header)
            
        data = [
            ['Base', 1.00, 1.00, 0.00, 0.00, 1.00],
            ['Best', 1.15, 0.95, 0.01, 0.005, 1.20],
            ['Worst', 0.85, 1.10, -0.01, -0.005, 0.80]
        ]
        
        for r, row_dat in enumerate(data):
            for c, val in enumerate(row_dat):
                ws_scen.write(r+1, c, val, fmt_calc)
                
        # Define Table Name: Scenario_Table!$A$2:$F$4
        workbook.define_name('Scenario_Table', f'=Scenario_Table!$A$2:$F${len(data)+1}')
        
        # ---------------------------------------------------------
        # 3. Depreciation Schedule Formula Sheet
        # ---------------------------------------------------------
        ws_depr = workbook.add_worksheet('Depreciation_Sched')
        # We need a matrix: Columns = Months, Rows = Capex Batches
        # Since we don't know exact future capex in Excel (it's dynamic), 
        # we will link Capex from Engine and waterfall it.
        # But this is circular if Engine depends on Depr. 
        # Solution: P&L depends on Depreciation. Capex usually input.
        # We will put Capex Input on this sheet or Engine and waterfall here.
        
        dates = pd.to_datetime(self.forecast_df['date'])
        
        # Header Row (Dates)
        ws_depr.write(0, 0, 'Date', fmt_header)
        ws_depr.write(1, 0, 'New Capex', fmt_header)
        
        for i, d in enumerate(dates):
            ws_depr.write(0, i+1, d.strftime('%b-%y'), fmt_month)
            # Link New Capex from Engine (Row 9 in Engine)
            # We assume Engine Column alignment (Col 1 is Date 1)
            # Engine Col Index = i + 1 (A is labels) -> B, C, D...
            # Excel col B is index 1.
            col_letter = xlsxwriter.utility.xl_col_to_name(i+1)
            ws_depr.write_formula(1, i+1, f'=Engine!{col_letter}9', fmt_curr) 
            
        # Waterfall
        ws_depr.write(2, 0, 'Depreciation Waterfall', fmt_header)
        # For each month T, Capex happened. Depr starts T.
        # Depr = IF(CurrentMonth >= T AND CurrentMonth < T+UsefulLife, Capex_T / UsefulLife, 0)
        
        for r_idx, d_start in enumerate(dates): # One row for each month's capex batch
            actual_row = r_idx + 3
            ws_depr.write(actual_row, 0, f'Batch {d_start.strftime("%b-%y")}', fmt_calc)
            
            # Capex Amount Cell reference: Formula is =Row2_Col(r_idx+1)
            capex_ref = f'{xlsxwriter.utility.xl_col_to_name(r_idx+1)}2'
            
            for c_idx, d_curr in enumerate(dates):
                actual_col = c_idx + 1
                # Formula logic:
                # If c_idx >= r_idx (current time >= batch time)
                # AND c_idx < r_idx + UsefulLife
                # Then Capex/Life
                
                # Note: UsefulLife is Named Range
                form = f'=IF(AND({c_idx}>={r_idx}, {c_idx}<{r_idx}+UsefulLife), {capex_ref}/UsefulLife, 0)'
                ws_depr.write_formula(actual_row, actual_col, form, fmt_num)

        # Total Depreciation Row
        total_row = len(dates) + 4
        ws_depr.write(total_row, 0, 'TOTAL DEPRECIATION', fmt_header)
        for i in range(len(dates)):
            col_letter = xlsxwriter.utility.xl_col_to_name(i+1)
            # Sum the waterfall rows
            ws_depr.write_formula(total_row, i+1, f'=SUM({col_letter}4:{col_letter}{total_row})', fmt_curr)
            
        # Define Named Range for Total Depr Row
        # DeprStream = Depreciation_Sched!$B$TotalRow:$End$TotalRow
        end_col_let = xlsxwriter.utility.xl_col_to_name(len(dates))
        workbook.define_name('DeprStream', f'=Depreciation_Sched!$B${total_row+1}:${end_col_let}${total_row+1}')

        # ---------------------------------------------------------
        # 4. Engine Sheet
        # ---------------------------------------------------------
        ws_eng = workbook.add_worksheet('Engine')
        labels = [
            'Month Index', 'Revenue', 'COGS', 'OpEx', 'Payroll', 
            'Headcount', 'EBITDA', 'Capex', 'Depreciation', 
            'EBIT', 'Tax', 'Net Income'
        ]
        
        ws_eng.write(0, 0, 'Metric', fmt_header)
        for r, l in enumerate(labels):
            ws_eng.write(r+1, 0, l, fmt_header)
            
        # Scenario Lookups
        # MATCH(ScenarioSelector, Scenario_Table[Scenario], 0)
        idx_match = 'MATCH(ScenarioSelector,INDEX(Scenario_Table,,1),0)'
        rev_mult = f'INDEX(Scenario_Table,{idx_match},2)'
        cogs_mult = f'INDEX(Scenario_Table,{idx_match},3)'
        vol_adj = f'INDEX(Scenario_Table,{idx_match},4)'
        price_adj = f'INDEX(Scenario_Table,{idx_match},5)'
        capex_mult = f'INDEX(Scenario_Table,{idx_match},6)'
        
        for c, date_val in enumerate(dates):
            col = c + 1
            col_let = xlsxwriter.utility.xl_col_to_name(col)
            
            # Header Date
            ws_eng.write(0, col, date_val.strftime('%b-%y'), fmt_month)
            
            # 1. Month Index
            ws_eng.write(1, col, c+1, fmt_num)
            
            # 2. Revenue
            # BaseRev * (1+Vol+Adj)^(t-1) * (1+Price+Adj)^(t-1) * Seas * Mult
            t = f'({col_let}2-1)' # t-1 so starts at 0 growth
            month_mod = f'MOD({col_let}2-1, 12)+1' # 1 to 12
            seas = f'INDEX(Seasonality, {month_mod})'
            
            rev_f = (f'=BaseRevenue * ((1+VolGrowth+{vol_adj})^{t}) '
                     f'* ((1+PriceGrowth+{price_adj})^{t}) * {seas} * {rev_mult}')
            ws_eng.write_formula(2, col, rev_f, fmt_curr)
            
            # 3. COGS
            ws_eng.write_formula(3, col, f'={col_let}3 * COGS_Pct * {cogs_mult}', fmt_curr)
            
            # 6. Headcount first (needed for payroll)
            # Start + Int(HiringRate * t)
            ws_eng.write_formula(6, col, f'=HC_Start + INT(HiringRate * {t})', fmt_num)
            
            # 5. Payroll
            ws_eng.write_formula(5, col, f'={col_let}7 * AvgSalary', fmt_curr)
            
            # 4. OpEx
            # Fixed + Var*Rev + Payroll
            ws_eng.write_formula(4, col, f'=FixedOpEx + (OpExVarPct * {col_let}3) + {col_let}6', fmt_curr)
            
            # 7. EBITDA
            ws_eng.write_formula(7, col, f'={col_let}3 - {col_let}4 - {col_let}5', fmt_curr)
            
            # 8. Capex
            # Pull from JSON schedule? We'll load the JSON value "base" and multiply by scenario
            # JSON schedule is date-keyed. Hard to formula-ize without a lookup table.
            # We will write the BASE value as a hard number here, multiplied by scenario mult formula.
            # "Semi-formula".
            base_capex = self.forecast_df.loc[c, 'capex']
            ws_eng.write_formula(8, col, f'={base_capex} * {capex_mult}', fmt_curr)
            
            # 9. Depreciation
            # Link to the Depreciation Waterfall Sheet Total Row
            # INDEX(DeprStream, Col)
            ws_eng.write_formula(9, col, f'=INDEX(DeprStream, {col})', fmt_curr)
            
            # 10. EBIT
            ws_eng.write_formula(10, col, f'={col_let}8 - {col_let}10', fmt_curr)
            
            # 11. Tax
            ws_eng.write_formula(11, col, f'=MAX(0, {col_let}11 * TaxRate)', fmt_curr)
            
            # 12. Net Income
            ws_eng.write_formula(12, col, f'={col_let}11 - {col_let}12', fmt_curr)

        # ---------------------------------------------------------
        # 5. Working Capital & Cash
        # ---------------------------------------------------------
        ws_wc = workbook.add_worksheet('Working_Capital')
        wc_lbls = ['Date', 'Revenue', 'COGS', 'OpEx', 'AR', 'Inventory', 'AP', 'Net WC', 'Change in WC', 'NetIncome', 'Depre', 'Capex', 'Cash Flow', 'Cash Balance']
        ws_wc.write_row(0, 0, wc_lbls, fmt_header)
        
        for c, date_val in enumerate(dates):
            r = c + 1
            # Link Data
            col_let = xlsxwriter.utility.xl_col_to_name(c+1) # Engine column
            
            ws_wc.write(r, 0, date_val.strftime('%b-%y'), fmt_month)
            ws_wc.write_formula(r, 1, f'=Engine!{col_let}3', fmt_curr) # Rev
            ws_wc.write_formula(r, 2, f'=Engine!{col_let}4', fmt_curr) # COGS
            
            # Drivers
            ws_wc.write_formula(r, 3, '=DSO', fmt_num)
            ws_wc.write_formula(r, 4, '=DSI', fmt_num)
            ws_wc.write_formula(r, 5, '=DPO', fmt_num)
            
            # AR = Rev / 365 * DSO (formula requested)
            ws_wc.write_formula(r, 6, f'=B{r+1} / 365 * D{r+1}', fmt_curr)
            # Inv = COGS / 365 * DSI
            ws_wc.write_formula(r, 7, f'=C{r+1} / 365 * E{r+1}', fmt_curr)
            # AP = COGS / 365 * DPO
            ws_wc.write_formula(r, 8, f'=C{r+1} / 365 * F{r+1}', fmt_curr)
            
            # Net WC = AR + Inv - AP
            ws_wc.write_formula(r, 9, f'=G{r+1} + H{r+1} - I{r+1}', fmt_curr)
            
            # Delta WC
            if r == 1:
                ws_wc.write_formula(r, 10, f'=J{r+1} - 0', fmt_curr)
            else:
                 ws_wc.write_formula(r, 10, f'=J{r+1} - J{r}', fmt_curr)

            # Link NI, Depr, Capex
            # NI is Engine Row 13
            ws_wc.write_formula(r, 11, f'=Engine!{col_let}13', fmt_curr) # Use correct index
            ws_wc.write_formula(r, 12, f'=Engine!{col_let}10', fmt_curr) # Depr
            ws_wc.write_formula(r, 13, f'=Engine!{col_let}9', fmt_curr) # Capex
                 
            # Cash Flow = NetIncome + Depr - DeltaWC - Capex
            ws_wc.write_formula(r, 14, f'=L{r+1} + M{r+1} - K{r+1} - N{r+1}', fmt_curr) 
            
            # Cash Balance
            if r == 1:
                ws_wc.write_formula(r, 15, f'=InitCash + O{r+1}', fmt_curr)
            else:
                ws_wc.write_formula(r, 15, f'=P{r} + O{r+1}', fmt_curr)

        # ---------------------------------------------------------
        # 6. Sensitivity (Matrix)
        # ---------------------------------------------------------
        ws_sens = workbook.add_worksheet('Sensitivity')
        ws_sens.write('A1', 'SENSITIVITY ANALYSIS: REVENUE', fmt_header)
        
        ws_sens.write('A3', 'Price \\ Volume', fmt_header)
        
        range_vals = [-0.10, -0.05, 0.00, 0.05, 0.10]
        # Column Headers (Volume Shift)
        for i, v in enumerate(range_vals):
            ws_sens.write(2, i+1, v, fmt_pct)
        # Row Headers (Price Shift)
        for i, p in enumerate(range_vals):
            ws_sens.write(i+3, 0, p, fmt_pct)
            
        # Matrix Formulas
        base_rev_ref = 'SUM(Engine!3:3)'
        
        for r, p in enumerate(range_vals):
            for c, v in enumerate(range_vals):
                p_cell = f'$A{r+4}'
                v_cell = f'{xlsxwriter.utility.xl_col_to_name(c+1)}$3'
                
                form = f'={base_rev_ref} * (1+{p_cell}) * (1+{v_cell})'
                ws_sens.write_formula(r+3, c+1, form, fmt_curr)

        # ---------------------------------------------------------
        # 7. Checks
        # ---------------------------------------------------------
        ws_chk = workbook.add_worksheet('Checks')
        ws_chk.write('A1', 'Validation Check', fmt_header)
        ws_chk.write('B1', 'Status', fmt_header)
        
        checks = [
            ('Cash is Positive', '=MIN(Working_Capital!P:P) > 0'), # P is Balance
            ('Revenue Match', '=SUM(Engine!3:3) > 0'),
            ('Balance Sheet Logic', '="Assets = Liab + Equity"'), 
            ('No Errors', '=SUM(IF(ISERROR(Engine!A1:Z100),1,0)) = 0')
        ]
        
        for i, (lbl, formula) in enumerate(checks):
            ws_chk.write(i+1, 0, lbl, fmt_calc)
            ws_chk.write_formula(i+1, 1, formula)
            
        writer.close()
        print(f"✅ FINAL FORMULA MODEL SAVED: {output_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hist_path = os.path.join(base_dir, 'data', 'raw', 'historical_financials.csv') # Dummy for init
    forecast_path = os.path.join(base_dir, 'data', 'processed', 'forecast_output.csv')
    output_path = os.path.join(base_dir, 'outputs', 'FPnA_Model_with_formulas.xlsx')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    exporter = ExportModule(hist_path if os.path.exists(hist_path) else forecast_path, forecast_path)
    exporter.create_excel_model(output_path)
