import requests as req
import pandas as pd
import time
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import box

console = Console()

class OptionDataAnalyzer:
    def get_option_chain_data(self, instrument_name: str, expiry_date: str, side: str) -> pd.DataFrame:
        """
        Fetch option chain data from NSE website based on input parameters.
        
        Parameters:
            instrument_name (str): The name of the instrument (e.g., NIFTY, BANKNIFTY).
            expiry_date (str): The expiration date of the options in YYYY-MM-DD format.
            side (str): The option type ('PE' for Put, 'CE' for Call).
        
        Returns:
            pd.DataFrame: DataFrame containing the instrument name, strike price, option side, and highest bid/ask price.
        """
        try:
            expiry_date_formatted = datetime.strptime(expiry_date, "%Y-%m-%d").strftime("%d-%b-%Y")
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
            raise ValueError("Invalid date format")

        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={instrument_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.nseindia.com",
        }
        
        session = req.Session()
        session.get("https://www.nseindia.com", headers=headers)
        data_list = []

        for _ in range(3):
            try:
                response = session.get(url, headers=headers)
                if response.status_code == 200 and response.text.startswith("{") and response.text.endswith("}"):
                    data = response.json()

                    if not data:
                        console.print("[red]No data retrieved. Check your inputs or try again later.[/red]")
                        return pd.DataFrame(columns=["instrument_name", "strike_price", "side", "bid/ask"])

                    if "records" not in data or "data" not in data["records"]:
                        console.print(f"[red]Instrument '{instrument_name}' not found. Please check the instrument name.[/red]")
                        raise TypeError("Invalid response structure")

                    option_data = data["records"]["data"]

                    # Dictionary to hold the highest bid/ask prices
                    highest_prices = {}

                    for item in option_data:
                        if item["expiryDate"] == expiry_date_formatted:
                            strike_price = item["strikePrice"]

                            if side not in ["PE", "CE"]:
                                console.print(f"[red]Invalid option side '{side}'. Please use 'PE' or 'CE'.[/red]")
                                raise ValueError(f"Invalid option side: {side}")

                            if side == "PE" and "PE" in item:
                                bid_price = item["PE"].get("bidprice", 0)
                                if strike_price not in highest_prices:
                                    highest_prices[strike_price] = {"highest_bid": bid_price}
                                else:
                                    highest_prices[strike_price]["highest_bid"] = max(highest_prices[strike_price]["highest_bid"], bid_price)

                            elif side == "CE" and "CE" in item:
                                ask_price = item["CE"].get("askPrice", 0)
                                if strike_price not in highest_prices:
                                    highest_prices[strike_price] = {"highest_ask": ask_price}
                                else:
                                    highest_prices[strike_price]["highest_ask"] = max(highest_prices[strike_price]["highest_ask"], ask_price)

                    for strike_price, prices in highest_prices.items():
                        if side == "PE":
                            data_list.append({
                                "instrument_name": instrument_name,
                                "strike_price": strike_price,
                                "side": "PE",
                                "bid/ask": round(prices.get("highest_bid", 0), 2)
                            })
                        elif side == "CE":
                            data_list.append({
                                "instrument_name": instrument_name,
                                "strike_price": strike_price,
                                "side": "CE",
                                "bid/ask": round(prices.get("highest_ask", 0), 2)
                            })

                    return pd.DataFrame(data_list)
                else:
                    console.print(f"[red]Failed to retrieve data: {response.status_code}[/red]")
            except req.RequestException as e:
                console.print(f"[red]Request failed: {e}[/red]")
            except ValueError as ve:
                console.print(f"[red]Failed to process data: {ve}[/red]")
                break
            time.sleep(2)

        console.print("[red]Failed to retrieve valid data after multiple attempts.[/red]")
        return pd.DataFrame(columns=["instrument_name", "strike_price", "side", "bid/ask"])



    def calculate_margin_and_premium(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate margin and premium earned for each option in the DataFrame.
        
        Parameters:
            data (pd.DataFrame): DataFrame containing option chain data.
        
        Returns:
            pd.DataFrame: DataFrame with additional columns for margin and premium.
        """
        
        try:
            data["bid/ask"] = pd.to_numeric(data["bid/ask"], errors='raise')
            data["margin_required"] = data["strike_price"] * 0.1 # mock, assume margin of 10%
            data["premium_earned"] = data["bid/ask"] * 75 # mock, general lot size in options market is assumed to be 75
        except ValueError as ve:
            console.print(f"[red]Error: Invalid data type for 'bid/ask'. {ve}[/red]")
            raise TypeError("Invalid data type for 'bid/ask'.") from ve
        except Exception as e:
            console.print(f"[red]Unexpected error calculating margin and premium: {e}[/red]")
            raise 
        return data


def validate_expiry_date(expiry_date: str) -> Optional[str]:
    try:
        datetime.strptime(expiry_date, "%Y-%m-%d")
        return expiry_date
    except ValueError:
        console.print("[red]Invalid expiry date format. Please enter the date in YYYY-MM-DD format.[/red]")
        return None


def run_cli():
    console.print("[cyan bold]Options Data Fetcher[/cyan bold]\n")
    instrument_name = Prompt.ask("[yellow]Enter the instrument name[/yellow] (e.g., NIFTY, BANKNIFTY)")
    expiry_date = None

    while not expiry_date:
        expiry_date_input = Prompt.ask("[yellow]Enter the expiry date[/yellow] (in YYYY-MM-DD format)")
        expiry_date = validate_expiry_date(expiry_date_input)

    side = Prompt.ask("[yellow]Enter the option type[/yellow] ([green]PE[/green] for Put, [green]CE[/green] for Call)", choices=["PE", "CE"])

    handler = OptionDataAnalyzer()
    
    console.print("\n[blue]Fetching option chain data...[/blue]")
    try:
        data = handler.get_option_chain_data(instrument_name, expiry_date, side)
    except ValueError:
        console.print("[red]Failed to retrieve option chain data due to invalid input. Exiting.[/red]")
        return

    if data.empty:
        console.print("[red]No data retrieved. Check your inputs or try again later.[/red]")
        return

    table = Table(title="Option Chain Data", box=box.SQUARE)
    table.add_column("Instrument", style="cyan", justify="center")
    table.add_column("Strike Price", style="magenta", justify="center")
    table.add_column("Side", style="green", justify="center")
    table.add_column("Bid/Ask Price", style="yellow", justify="center")
    
    for _, row in data.iterrows():
        table.add_row(str(row["instrument_name"]), str(row["strike_price"]), row["side"], f"{row['bid/ask']:.2f}")
    
    console.print(table)

    console.print("\n[blue]Calculating margin and premium...[/blue]")
    data_with_margin = handler.calculate_margin_and_premium(data)

    result_table = Table(title="Option Data with Margin and Premium", box=box.SQUARE)
    result_table.add_column("Instrument", style="cyan", justify="center")
    result_table.add_column("Strike Price", style="magenta", justify="center")
    result_table.add_column("Side", style="green", justify="center")
    result_table.add_column("Bid/Ask Price", style="yellow", justify="center")
    result_table.add_column("Margin Required", style="bright_red", justify="center")
    result_table.add_column("Premium Earned", style="bright_green", justify="center")

    for _, row in data_with_margin.iterrows():
        result_table.add_row(
            str(row["instrument_name"]),
            str(row["strike_price"]),
            row["side"],
            f"{row['bid/ask']:.2f}",
            f"{row['margin_required']:.2f}",
            f"{row['premium_earned']:.2f}"
        )
    
    console.print(result_table)


if __name__ == "__main__":
    run_cli()
