"""
P3 Financial Forecasting Simulator - Main Entry Point
Run this file to execute the complete forecasting pipeline.
"""

import os
import sys
import shutil

def run_pipeline():
    """Execute the complete FP&A forecasting pipeline."""
    
    print("=" * 60)
    print("🚀 P3 FINANCIAL FORECASTING SIMULATOR")
    print("=" * 60)
    print("\nGenerating driver-based financial forecasts...")
    print("This will produce:")
    print("  ✓ Historical financial statements")
    print("  ✓ 36-month forecasts (Base/Best/Worst scenarios)")
    print("  ✓ Scenario comparison & KPI summary")
    print("  ✓ Excel model with formulas")
    print("\n" + "-" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure output directories exist
    os.makedirs(os.path.join(base_dir, 'outputs'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'data', 'processed'), exist_ok=True)
    
    # Step 1: Generate dimension tables (date dimension)
    print("\n[1/4] 📅 Generating dimension tables...")
    data_gen_path = os.path.join(base_dir, 'src', 'data_generator.py')
    if os.system(f'python "{data_gen_path}"') != 0:
        print("❌ Data generation failed")
        return 1
    
    # Step 2: Run forecast engine (deterministic driver-based)
    print("\n[2/4] 🔮 Running forecast engine...")
    forecast_path = os.path.join(base_dir, 'src', 'forecast_engine.py')
    if os.system(f'python "{forecast_path}"') != 0:
        print("❌ Forecast engine failed")
        return 1
    
    # Step 3: Export to Excel with formulas
    print("\n[3/4] 📊 Exporting Excel model...")
    export_path = os.path.join(base_dir, 'src', 'export_module.py')
    if os.system(f'python "{export_path}"') != 0:
        print("❌ Excel export failed")
        return 1
    
    # Step 4: Generate insights report
    print("\n[4/4] 📝 Generating insights report...")
    insights_path = os.path.join(base_dir, 'src', 'insight_generator.py')
    os.system(f'python "{insights_path}"')  # Non-critical, don't fail on error
    
    # Copy key outputs to outputs folder for easy access
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    outputs_dir = os.path.join(base_dir, 'outputs')
    
    files_to_copy = {
        'forecast_output.csv': 'base_forecast.csv',
        'scenario_comparison.csv': 'scenario_summary.csv',
        'model_metrics.csv': 'kpi_summary.csv'
    }
    
    for src_name, dest_name in files_to_copy.items():
        src = os.path.join(processed_dir, src_name)
        dest = os.path.join(outputs_dir, dest_name)
        if os.path.exists(src):
            shutil.copy2(src, dest)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ FORECAST COMPLETED")
    print("=" * 60)
    print("\n📂 Output Files:")
    print(f"  → {os.path.join('outputs', 'base_forecast.csv')}")
    print(f"  → {os.path.join('outputs', 'scenario_summary.csv')}")
    print(f"  → {os.path.join('outputs', 'kpi_summary.csv')}")
    print(f"  → {os.path.join('outputs', 'FPnA_Model_with_formulas.xlsx')}")
    print(f"\n📊 View Excel model for interactive scenario analysis")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(run_pipeline())
