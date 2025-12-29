"""
DATA MANAGER - Centralized data handling with retry logic
=========================================================
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import List, Tuple
import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages all data operations for backtesting."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def fetch_stock_data(
        self, 
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        max_retries: int = 3
    ) -> pd.DataFrame:
        """
        Download stock data with retry logic.
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL')
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            interval: '1d', '1h', '5m'
            max_retries: Number of retry attempts
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        for attempt in range(max_retries):
            try:
                # Use Ticker object (more reliable)
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )
                
                if df.empty:
                    if attempt < max_retries - 1:
                        logger.warning(f"Empty data on attempt {attempt+1}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        raise ValueError(f"No data returned for {symbol} after {max_retries} attempts")
                
                # Standardize column names
                df.columns = [col.lower() for col in df.columns]
                
                # Handle missing data
                df = df.ffill(limit=3).dropna()
                
                logger.info(f"✅ Downloaded {len(df)} bars for {symbol}")
                return df
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt+1} failed: {str(e)}, retrying...")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to fetch {symbol} after {max_retries} attempts: {str(e)}")
                    raise
            
    def split_train_test(
        self,
        data: pd.DataFrame,
        train_pct: float = 0.7,
        validation_pct: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically into train/val/test.
        
        Returns:
            (train_data, validation_data, test_data)
        """
        n = len(data)
        train_end = int(n * train_pct)
        val_end = int(n * (train_pct + validation_pct))
        
        train = data.iloc[:train_end].copy()
        validation = data.iloc[train_end:val_end].copy()
        test = data.iloc[val_end:].copy()
        
        logger.info(f"Split: Train={len(train)}, Val={len(validation)}, Test={len(test)}")
        return train, validation, test
        
    def get_multiple_symbols(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> dict:
        """Fetch data for multiple symbols."""
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.fetch_stock_data(symbol, start_date, end_date)
            except Exception as e:
                logger.error(f"Skipping {symbol}: {str(e)}")
        return result


if __name__ == "__main__":
    dm = DataManager()
    aapl = dm.fetch_stock_data('AAPL', '2023-01-01', '2023-12-31')
    print("\n📊 AAPL Data:")
    print(aapl.head())
    print(f"\nShape: {aapl.shape}")
    
    train, val, test = dm.split_train_test(aapl)
    print(f"\n✂️ Train: {len(train)} days")
    print(f"Val: {len(val)} days")
    print(f"Test: {len(test)} days")
