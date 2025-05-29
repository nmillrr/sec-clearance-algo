import pandas as pd
from sec_api import FullTextSearchApi
from aylienapiclient.textapi import Client as AylienClient
import yfinance as yf
import logging
from datetime import datetime, timedelta
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your API keys
SEC_API_KEY = "YOUR_SEC_API_KEY"
AYLIEN_APP_ID = "YOUR_AYLIEN_APP_ID"
AYLIEN_API_KEY = "YOUR_AYLIEN_API_KEY"

def find_clearance_announcements(start_date="2001-01-01", end_date=datetime.now().strftime("%Y-%m-%d")):
    """
    Search for SEC filings mentioning investigation closures.
    Returns list of filings with company CIK, ticker, date, and text snippet.
    """
    try:
        full_text_api = FullTextSearchApi(api_key=SEC_API_KEY)
        keywords = ['SEC investigation closed', 'no further action', 'cleared by SEC', 'SEC concluded no violation']
        query = " OR ".join(f'"{keyword}"' for keyword in keywords)
        search_query = {
            "query": query,
            "formTypes": ['8-K', '10-K', '10-Q'],
            "startDate": start_date,
            "endDate": end_date
        }
        filings = full_text_api.get_filings(search_query)
        results = []
        for filing in filings.get('filings', []):
            results.append({
                'cik': filing.get('cik'),
                'ticker': filing.get('ticker', 'Unknown'),
                'filing_date': filing.get('filedAt'),
                'form_type': filing.get('formType'),
                'text_snippet': filing.get('description', '')
            })
        logging.info(f"Found {len(results)} clearance announcements")
        return results
    except Exception as e:
        logging.error(f"Error in find_clearance_announcements: {e}")
        return []

def get_news_sentiment(company_name, ticker, start_date, end_date):
    """
    Fetch news sentiment for a company within a date range.
    Returns average sentiment score and article details.
    """
    try:
        aylien_client = AylienClient(AYLIEN_APP_ID, AYLIEN_API_KEY)
        start = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=7)
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=7)
        articles = aylien_client.Publish({
            'q': f"{company_name} OR {ticker}",
            'published_at_start': start.strftime("%Y-%m-%d"),
            'published_at_end': end.strftime("%Y-%m-%d"),
            'language': ['en']
        })
        sentiment_scores = []
        for article in articles.get('stories', []):
            sentiment = article.get('sentiment', {}).get('polarity', 'neutral')
            score = 1 if sentiment == 'positive' else -1 if sentiment == 'negative' else 0
            sentiment_scores.append({
                'title': article.get('title', ''),
                'sentiment': sentiment,
                'score': score,
                'date': article.get('published_at')
            })
        avg_score = sum(s['score'] for s in sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        logging.info(f"Average sentiment for {company_name}: {avg_score}")
        return {'articles': sentiment_scores, 'average_sentiment': avg_score}
    except Exception as e:
        logging.error(f"Error in get_news_sentiment: {e}")
        return {'articles': [], 'average_sentiment': 0}

def compile_strategy_data():
    """
    Combine SEC filings and news sentiment data.
    Returns dataset with investigation and clearance events.
    """
    try:
        clearance_filings = find_clearance_announcements()
        data = []
        for filing in clearance_filings:
            cik = filing['cik']
            t2 = filing['filing_date']
            ticker = filing['ticker']
            # Search for earlier investigation announcement
            full_text_api = FullTextSearchApi(api_key=SEC_API_KEY)
            keywords = ['SEC investigation', 'under investigation by SEC', 'received a subpoena from SEC']
            query = " OR ".join(f'"{keyword}"' for keyword in keywords)
            search_query = {
                "query": query,
                "formTypes": ['8-K', '10-K', '10-Q'],
                "startDate": "2001-01-01",
                "endDate": t2,
                "cik": cik
            }
            earlier_filings = full_text_api.get_filings(search_query)
            t1 = None
            for ef in earlier_filings.get('filings', []):
                if ef.get('filedAt') < t2:
                    t1 = ef.get('filedAt')
                    break
            # Get news sentiment around T2
            sentiment = get_news_sentiment(f"CIK:{cik}", ticker, t2, t2)
            data.append({
                'cik': cik,
                'ticker': ticker,
                't1': t1,
                't2': t2,
                'sentiment_t2': sentiment['average_sentiment'],
                'articles_t2': sentiment['articles']
            })
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"Error in compile_strategy_data: {e}")
        return pd.DataFrame()

def get_stock_prices(ticker, start_date, end_date):
    """
    Fetch historical stock prices using yfinance.
    Returns DataFrame with daily prices.
    """
    try:
        start = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        end = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
        stock = yf.Ticker(ticker)
        prices = stock.history(start=start, end=end)
        if prices.empty:
            logging.warning(f"No price data for {ticker}")
            return pd.DataFrame()
        return prices[['Open', 'Close', 'High', 'Low']]
    except Exception as e:
        logging.error(f"Error in get_stock_prices: {e}")
        return pd.DataFrame()

def backtest_strategy(data):
    """
    Backtest the strategy by simulating trades.
    Returns performance metrics and visualizations.
    """
    try:
        results = []
        for _, row in data.iterrows():
            if row['ticker'] == 'Unknown' or pd.isna(row['t2']):
                continue
            prices = get_stock_prices(row['ticker'], row['t2'], row['t2'])
            if prices.empty:
                continue
            t2_date = datetime.strptime(row['t2'], "%Y-%m-%d")
            buy_date = (t2_date + timedelta(days=1)).strftime("%Y-%m-%d")
            sell_date = (t2_date + timedelta(days=30)).strftime("%Y-%m-%d")
            buy_price = prices.loc[prices.index >= buy_date, 'Close'].iloc[0] if buy_date in prices.index else None
            sell_price = prices.loc[prices.index >= sell_date, 'Close'].iloc[0] if sell_date in prices.index else None
            if buy_price and sell_price:
                roi = (sell_price - buy_price) / buy_price * 100
                results.append({
                    'ticker': row['ticker'],
                    'buy_date': buy_date,
                    'sell_date': sell_date,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'roi': roi
                })
        results_df = pd.DataFrame(results)
        if results_df.empty:
            logging.info("No valid trades found")
            return {}
        metrics = {
            'total_trades': len(results_df),
            'average_roi': results_df['roi'].mean(),
            'win_rate': len(results_df[results_df['roi'] > 0]) / len(results_df) * 100
        }
        logging.info(f"Backtest metrics: {metrics}")
        return metrics
    except Exception as e:
        logging.error(f"Error in backtest_strategy: {e}")
        return {}

def main():
    """
    Main function to run the SEC clearance trading strategy.
    """
    logging.info("Starting SEC clearance trading strategy")
    data = compile_strategy_data()
    if not data.empty:
        metrics = backtest_strategy(data)
        print("Backtest Results:", metrics)
    else:
        print("No data found for backtesting")

if __name__ == "__main__":
    main()