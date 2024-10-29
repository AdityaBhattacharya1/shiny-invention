import yfinance as yf
import pandas as pd
from rich.console import Console
from rich.table import Table
from datetime import datetime


class OptionDataAnalyzer:
    def __init__(self, instrument_name: str):
        self.instrument_name = instrument_name
        self.stock = yf.Ticker(instrument_name)

    def get_option_chain_data(self, expiry_date: str, side: str) -> pd.DataFrame:
        """
        Retrieve option chain data for the specified expiry date and side.

        Parameters:
            expiry_date (str): Expiration date in YYYY-MM-DD format.
            side (str): Option type ("PE" for Put and "CE" for Call).

        Returns:
            pd.DataFrame: DataFrame containing instrument_name, strike_price, side, and bid/ask.
        """
        if not self._is_valid_date(expiry_date):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        available_expiries = self.stock.options

        if expiry_date not in available_expiries:
            raise ValueError(
                f"Expiration '{expiry_date}' cannot be found. Available expirations are: {available_expiries}"
            )

        option_chain = self.stock.option_chain(expiry_date)

        if side == "PE":
            options_data = option_chain.puts
            options_data["bid/ask"] = options_data["bid"]
        elif side == "CE":
            options_data = option_chain.calls
            options_data["bid/ask"] = options_data["ask"]
        else:
            raise ValueError("Invalid side value. Use 'PE' for Put or 'CE' for Call.")

        options_summary = (
            options_data.groupby("strike").agg({"bid/ask": "max"}).reset_index()
        )
        options_summary["instrument_name"] = self.instrument_name
        options_summary["side"] = side
        options_summary.rename(columns={"strike": "strike_price"}, inplace=True)
        return options_summary[["instrument_name", "strike_price", "side", "bid/ask"]]



def main():
    console = Console()
    console.print("[bold green]Welcome to Option Data Analyzer![/bold green]")

    instrument_name = console.input("Enter the instrument name (e.g., 'MSFT'): ")
    expiry_date = console.input("Enter the expiry date (YYYY-MM-DD): ")
    side = (
        console.input("Enter the option type ('PE' for Put, 'CE' for Call): ")
        .strip()
        .upper()
    )

    analyzer = OptionDataAnalyzer(instrument_name)


if __name__ == "__main__":
    main()
