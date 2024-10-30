# Option Data Analyzer

## Overview

The **Option Data Analyzer** is a Python application that retrieves, processes, and analyzes options chain data for specified financial instruments using web scraping. It allows users to specify an instrument (e.g., NIFTY or BANKNIFTY), an expiry date for options, and the type of option (Call or Put). The application then displays the highest bid or ask prices, calculates margin requirements, and determines premium earned based on the option data.

For this project I have scraped the NSE website instead of using Upstox, Fyers, etc. APIs since my objective for this project was to create an application that could work absolutely decoupled to any one particular user. In the case of Upstox, Fyers, KiteConnect, etc., a user would have to enter their PAN card credentials and other sensitive data to third party providers just to access financial data; thus coupling the usage of the application to a user's sensitive data for API key generation. In spirit of financial independence and general open source software, I decided against using such third parties so that running this application would require _zero_ sign-ups/log-ins. Cheers!

## File Structure

```sh
.
├── README.md
├── requirements.txt
└── src
    ├── __tests__
    │   ├── __init__.py
    │   └── test.py
    └── app
        ├── __init__.py
        └── options_data_fetcher.py
```

## Function Descriptions

### 1. `get_option_chain_data(self, expiry_date: str, side: str) -> pd.DataFrame`

#### Purpose

This function retrieves option chain data for a specified instrument on a given expiry date and returns the highest bid price for put options (PE) or the highest ask price for call options (CE).

#### Assumptions

-   The instrument name is a valid ticker symbol supported by NSE and is available via NSE's APIs.
-   The expiry date must be available for the specified instrument.
-   The side parameter must be either "PE" or "CE".

#### API Information

-   This function utilizes the `requests` library to dynamically scrape data from the NSE website and parse it into a processable format.

#### Processing

1. The function checks if the expiry date is valid using `validate_expiry_date` function.
2. It fetches the option chain data from the website using a GET request.
3. Depending on the `side`, it selects the highest `bid` for puts or the highest `ask` for calls and organizes this data into a DataFrame with columns: `instrument_name`, `strike_price`, `side`, and `bid/ask`.

#### Output Example

```plaintext
instrument_name | strike_price | side | bid/ask
-------------------------------------------------
NIFTY          | 19500       | CE   | 110
NIFTY          | 19600       | CE   | 160
```

### 2. `calculate_margin_and_premium(self, data: pd.DataFrame) -> pd.DataFrame`

#### Purpose

This function calculates the required margin and the premium earned for each option contract based on the bid or ask price.

#### Assumptions

-   A fixed lot size of 100 is assumed for the calculation of premiums.
-   A margin percentage (10% in this case) is assumed for margin calculations.

#### Processing

1. The function iterates through each row of the DataFrame.
2. For each option contract:
    - It calculates the premium earned by multiplying the bid/ask price by the lot size.
    - It calculates the margin required by multiplying the bid/ask price by the margin percentage and lot size.
3. The results are appended as new columns `margin_required` and `premium_earned`.

#### Output Example

```plaintext
instrument_name | strike_price | side | bid/ask | margin_required | premium_earned
-------------------------------------------------------------------------------------
NIFTY          | 19500       | CE   | 110      | 1100            | 11000
NIFTY          | 19600       | CE   | 160      | 1600            | 16000
```

### 3. `validate_expiry_date(expiry_date: str) -> Optional[str]`

#### Purpose

This function checks if a given date string is in the correct format (`YYYY-MM-DD`). If not, it attempts to convert it to the specific format.

#### Processing

-   It attempts to parse the date string using `datetime.strptime`.
-   If successful, it returns `True`; if not, it returns `False`.

#### Processing

-   It creates a table with columns derived from the DataFrame.
-   It iterates through each row to populate the table and prints it to the console.

### 5. `run_cli()`

#### Purpose

The main function serves as the entry point for the application. It is also where all the CLI code is written using the `rich` python library.

#### Processing

1. It prompts the user to input the instrument name, expiry date, and option type (PE/CE).
2. It creates an instance of `OptionDataAnalyzer` and calls the `get_option_chain_data` method.
3. It then calls `calculate_margin_and_premium` to get the financial calculations.
4. Finally, it displays the results using the `run_cli` function and handles any potential errors with appropriate messages.

## AI/LLM Usage

I have used ChatGPT to better understand what option chains are and what possible free and open-source alternatives I had to using Upstox, Fyers, and other third party financial data providers. Additionally, ChatGPT also helped me in the generation of this README file and add in relevant documentation on the basis of the code. Finally, I used ChatGPT to hint me with possible edge cases for this application which I then used in unit testing.

## Running the Application

```sh
# Clone the repo
git clone https://github.com/AdityaBhattacharya1/shiny-invention.git
cd shiny-invention

# To run the CLI App
pip install -r requirements.txt
python src/app/options_data_fetcher.py

# To run tests
pytest src/__tests__/test.py -v
```

## Conclusion

The **Option Data Analyzer** simplifies the process of analyzing options data by scraping essential data from the NSE website and providing users with a structured and informative output. It enables efficient decision-making for traders and analysts in the financial markets.
