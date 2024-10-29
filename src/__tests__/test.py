from app.options_data_fetcher import OptionDataAnalyzer
import unittest
import pandas as pd

class TestOptionsDataHandler(unittest.TestCase):

    def setUp(self):
        self.handler = OptionDataAnalyzer("MSFT")

    def test_valid_get_option_chain_data_ce(self):
        result = self.handler.get_option_chain_data("2024-11-01", "CE")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn("CE", result["side"].values)

    def test_valid_get_option_chain_data_pe(self):
        result = self.handler.get_option_chain_data( "2024-11-01", "PE")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertIn("PE", result["side"].values)


    def test_invalid_expiry_date_format(self):
        with self.assertRaises(ValueError) as context:
            self.handler.get_option_chain_data( "11/01/2024", "CE")
        self.assertEqual(
            str(context.exception), "Invalid date format. Please use YYYY-MM-DD."
        )

    def test_expiry_date_not_found(self):
        with self.assertRaises(ValueError) as context:
            self.handler.get_option_chain_data( "2024-10-01", "CE")
        self.assertIn("cannot be found", str(context.exception))

    def test_valid_calculate_margin_and_premium(self):
        data = pd.DataFrame(
            {
                "instrument_name": ["NIFTY", "NIFTY"],
                "strike_price": [19500, 19600],
                "side": ["CE", "PE"],
                "bid/ask": [2300.00, 0.65],
            }
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertIn("margin_required", result.columns)
        self.assertIn("premium_earned", result.columns)
        self.assertIsInstance(result["margin_required"].iloc[0], float)
        self.assertIsInstance(result["premium_earned"].iloc[0], float)

    def test_calculate_margin_and_premium_empty_dataframe(self):
        data = pd.DataFrame(
            columns=["instrument_name", "strike_price", "side", "bid/ask"]
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertTrue(result.empty)

    def test_calculate_margin_and_premium_invalid_data(self):
        data = pd.DataFrame(
            {
                "instrument_name": ["NIFTY"],
                "strike_price": [19500],
                "side": ["CE"],
                "bid/ask": ["not a float"],  # Invalid bid/ask data
            }
        )
        with self.assertRaises(TypeError):
            self.handler.calculate_margin_and_premium(data)

    def test_get_option_chain_data_invalid_side(self):
        with self.assertRaises(ValueError) as context:
            self.handler.get_option_chain_data("2024-11-01", "INVALID_SIDE")
        self.assertEqual(
            str(context.exception), "Invalid side value. Use 'PE' for Put or 'CE' for Call."
        )

    def test_calculate_margin_and_premium_large_values(self):
        data = pd.DataFrame(
            {
                "instrument_name": ["NIFTY"] * 5,
                "strike_price": [20000, 20500, 21000, 21500, 22000],
                "side": ["CE", "CE", "CE", "PE", "PE"],
                "bid/ask": [2500.00, 2600.50, 2700.75, 300.50, 310.60],
            }
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertIsInstance(
            result["margin_required"].iloc[0], float
        )  # Check one of the margins
        self.assertIsInstance(
            result["premium_earned"].iloc[0], float
        )  # Check one of the premiums

    def test_get_option_chain_data_non_existent_expiry(self):
        with self.assertRaises(ValueError) as context:
            self.handler.get_option_chain_data("2023-10-01", "CE")
        self.assertIn("cannot be found", str(context.exception))

    def test_edge_case_get_option_chain_data(self):
        result = self.handler.get_option_chain_data(
            "2024-12-20", "CE"
        )  
        self.assertIsInstance(result, pd.DataFrame)

    def test_edge_case_calculate_margin_and_premium(self):
        data = pd.DataFrame(
            {
                "instrument_name": ["BANKNIFTY"] * 3,
                "strike_price": [44000, 44500, 45000],
                "side": ["CE", "PE", "CE"],
                "bid/ask": [1500.00, 2000.00, 2500.00],
            }
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertGreater(
            result["margin_required"].sum(), 0
        )  # Ensure margin calculations are positive
        self.assertGreater(
            result["premium_earned"].sum(), 0
        )  # Ensure premiums are positive

    def test_data_type_validation(self):
        data = pd.DataFrame(
            {
                "instrument_name": ["NIFTY"],
                "strike_price": [19500],
                "side": ["CE"],
                "bid/ask": [0.75],
            }
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertIsInstance(
            result["margin_required"].iloc[0], float
        )  

    def test_empty_dataframe_in_calculate_margin(self):
        data = pd.DataFrame(
            columns=["instrument_name", "strike_price", "side", "bid/ask"]
        )
        result = self.handler.calculate_margin_and_premium(data)
        self.assertTrue(result.empty)

    def test_invalid_margin_api_response(self):
        with self.assertRaises(Exception) as context:
            self.handler.calculate_margin_and_premium(None)
        # self.assertIn("Invalid data", str(context.exception))


if __name__ == "__main__":
    unittest.main()