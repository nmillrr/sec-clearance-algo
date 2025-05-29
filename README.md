# SEC Clearance Trading Strategy

This repository implements a quantitative trading strategy that identifies opportunities to buy stocks at a dip caused by negative press from SEC investigations, then sell after the company is cleared by the SEC, anticipating a price rebound. The strategy leverages SEC filings, news sentiment analysis, and historical stock prices to backtest trading performance.

## Overview

The strategy is based on the observation that stocks often dip when the press reports an SEC investigation, but may rebound if the SEC later clears the company. The algorithm:
- Uses the [sec-api.io](https://sec-api.io/) API to find SEC filings (e.g., Form 8-K) mentioning investigations and clearances.
- Analyzes news sentiment around clearance announcements using the [AYLIEN News API](https://aylien.com/).
- Fetches historical stock prices via [yfinance](https://github.com/ranaroussi/yfinance) to backtest the strategy.
- Simulates buying stocks the day after a clearance announcement and selling 30 days later to capture the rebound.

This project is intended for educational purposes and to foster collaboration in the algorithmic trading community. It is not financial advice.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **API Keys**:
  - Obtain a free API key from [sec-api.io](https://sec-api.io/) for accessing SEC filings.
  - Sign up for a free trial API key from [AYLIEN News API](https://aylien.com/) for sentiment analysis.
- **Dependencies**: Install required Python libraries listed in `requirements.txt`.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nmillrr/sec-clearance-trading-strategy.git
   cd sec-clearance-trading-strategy
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   - Open `sec_clearance_strategy.py` and replace the following placeholders with your API keys:
     ```python
     SEC_API_KEY = "YOUR_SEC_API_KEY"
     AYLIEN_APP_ID = "YOUR_AYLIEN_APP_ID"
     AYLIEN_API_KEY = "YOUR_AYLIEN_API_KEY"
     ```
   - Obtain keys from:
     - [sec-api.io](https://sec-api.io/) for `SEC_API_KEY`.
     - [AYLIEN](https://aylien.com/) for `AYLIEN_APP_ID` and `AYLIEN_API_KEY`.

## Usage

Run the main script to execute the strategy and backtest it on historical data:

```bash
python sec_clearance_strategy.py
```

The script will:
- Query SEC filings for clearance announcements (T2 events) from 2001 to the present.
- Optionally search for earlier investigation announcements (T1 events).
- Fetch news sentiment around clearance dates.
- Backtest the strategy by simulating trades (buy at T2+1 day, sell after 30 days).
- Output performance metrics, including total trades, average ROI, and win rate.

### Example Output
```
2025-05-28 21:24:00 - INFO - Starting SEC clearance trading strategy
2025-05-28 21:24:10 - INFO - Found 25 clearance announcements
2025-05-28 21:24:20 - INFO - Average sentiment for CIK:1234567890: -0.3
Backtest Results: {'total_trades': 15, 'average_roi': 2.5, 'win_rate': 60.0}
```

## Project Structure

- `sec_clearance_strategy.py`: Main script implementing the trading strategy.
- `requirements.txt`: List of Python dependencies.
- `README.md`: Project documentation (this file).

## Backtesting Details

The backtesting process:
- Identifies companies cleared by the SEC (T2 events).
- Fetches historical stock prices around T2 using yfinance.
- Simulates buying the stock the day after T2 and selling 30 days later.
- Calculates performance metrics:
  - **Total Trades**: Number of valid trades executed.
  - **Average ROI**: Average return on investment across trades.
  - **Win Rate**: Percentage of trades with positive returns.

Note: The strategy assumes the stock is still depressed at T2 due to earlier negative press. Historical data may introduce survivorship bias, as only cleared companies are analyzed.

## Limitations

- **Data Availability**: SEC investigations may not always be disclosed in filings, and news sentiment data depends on API coverage.
- **Timing**: The strategy buys at T2, which may not always capture the dip if the market has already reacted.
- **API Costs**: Free API tiers have limits; consider upgrading for extensive use.
- **Live Trading**: The script is designed for backtesting. Live trading requires real-time monitoring and brokerage API integration.

## Contributing

Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

Join discussions on Reddit’s [r/algotrading](https://www.reddit.com/r/algotrading/) or GitHub’s [algorithmic-trading topic](https://github.com/topics/algorithmic-trading) to share ideas.

## License

This project is licensed under the MIT License.

## Disclaimer

This project is for educational purposes only and does not constitute financial advice. Trading involves significant risk, and past performance does not guarantee future results. Use at your own risk.