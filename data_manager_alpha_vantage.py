"""
DATA MANAGER - Alpha Vantage fallback
"""
import pandas as pd
import requests
import time

class DataManager:
    def __init__(self, alpha_vantage_key=None):
        self.av_key = alpha_vantage_key or "demo"  # Free demo key
        
    def fetch_from_alpha_vantage(self, symbol, outputsize='full'):
        """Fetch from Alpha Vantage API."""
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.av_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            df = pd.DataFrame.from_dict(
                data['Time Series (Daily)'], 
                orient='index'
            )
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)
            
            return df
        else:
            raise ValueError(f"Alpha Vantage error: {data}")
