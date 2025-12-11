import unittest
import os
import pandas as pd

class TestProjectStructure(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

    def test_dim_date_exists(self):
        path = os.path.join(self.base_dir, 'data', 'processed', 'dim_date.csv')
        self.assertTrue(os.path.exists(path), "DimDate CSV missing")
        df = pd.read_csv(path)
        self.assertGreater(len(df), 0, "DimDate is empty")
        self.assertIn('Date', df.columns, "DimDate missing Date column")

    def test_model_metrics_exists(self):
        path = os.path.join(self.base_dir, 'data', 'processed', 'model_metrics.csv')
        self.assertTrue(os.path.exists(path), "Model Metrics CSV missing")
        df = pd.read_csv(path)
        required = ['Series', 'ModelName', 'MAPE', 'RMSE']
        for col in required:
            self.assertIn(col, df.columns)

    def test_scenario_output_exists(self):
        path = os.path.join(self.base_dir, 'data', 'processed', 'scenario_output.csv')
        self.assertTrue(os.path.exists(path), "Scenario Output CSV missing")
        df = pd.read_csv(path)
        self.assertGreater(len(df), 0)
        self.assertIn('Scenario', df.columns)
        self.assertIn('EBITDA', df.columns)

    def test_excel_export_exists(self):
        path = os.path.join(self.base_dir, 'outputs', 'FPnA_Model.xlsx')
        self.assertTrue(os.path.exists(path), "Excel Model missing")

    def test_insights_exists(self):
        path = os.path.join(self.base_dir, 'outputs', 'insights_report.txt')
        self.assertTrue(os.path.exists(path), "Insights Report missing")

if __name__ == '__main__':
    unittest.main()
