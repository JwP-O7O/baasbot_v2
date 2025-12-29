"""
DATA MANAGER - Improved synthetic data
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
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def _generate_realistic_synthetic_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Generate REALISTIC synthetic data with trends and regimes."""
        logger.info(f"Generating realistic synthetic data for {symbol}")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(dates)
        
        # Seed based on symbol for consistency
        np.random.seed(hash(symbol) % 2**32)
        
        # Create regime periods (bull/bear/sideways)
        regime_length = n // 4  # 4 regimes over period
        regimes = []
        
        for i in range(4):
            regime_type = np.random.choice(['bull', 'bear', 'sideways'])
            regimes.extend([regime_type] * regime_length)
        
        # Pad to exact length
        while len(regimes) < n:
            regimes.append(regimes[-1])
        regimes = regimes[:n]
        
        # Generate prices based on regimes
        S0 = 100
        prices = [S0]
        
        for i in range(1, n):
            regime = regimes[i]
            
            if regime == 'bull':
                mu = 0.0008  # 0.08% daily = ~20% annual
                sigma = 0.012
            elif regime == 'bear':
                mu = -0.0005  # -0.05% daily = ~-12% annual
                sigma = 0.018
            else:  # sideways
                mu = 0.0001
                sigma = 0.008
            
            # Add momentum (trend persistence)
            if i > 1:
                momentum = (prices[-1] / prices[-2] - 1) * 0.3
                mu += momentum
            
            ret = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + ret))
        
        prices = np.array(prices)
        
        # Generate OHLCV
        close = prices
        high = close * (1 + np.abs(np.random.normal(0, 0.005, n)))
        low = close * (1 - np.abs(np.random.normal(0, 0.005, n)))
        open_price = np.roll(close, 1) * (1 + np.random.normal(0, 0.003, n))
        open_price[0] = close[0]
        
        # Volume increases during volatile periods
        base_volume = 5000000
        volatility = np.abs(np.diff(np.log(prices), prepend=np.log(prices[0])))
        volume = base_volume * (1 + volatility * 20) * np.random.lognormal(0, 0.3, n)
        
        df = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        logger.info(f"  Generated with {len(set(regimes))} market regimes")
        return df
        
    def fetch_stock_data(
        self, 
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        use_synthetic_on_fail: bool = True
    ) -> pd.DataFrame:
        """Download with improved synthetic fallback."""
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        # Try yfinance
        for attempt in range(3):
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, interval=interval)
                
                if not df.empty:
                    df.columns = [col.lower() for col in df.columns]
                    df = df.ffill(limit=3).dropna()
                    logger.info(f"✅ Downloaded {len(df)} bars from Yahoo Finance")
                    return df
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(2)
        
        # Fallback to REALISTIC synthetic
        if use_synthetic_on_fail:
            logger.warning(f"Using REALISTIC synthetic data for {symbol}")
            return self._generate_realistic_synthetic_data(symbol, start_date, end_date)
        else:
            raise ValueError(f"Failed to fetch {symbol}")
            
    def split_train_test(
        self,
        data: pd.DataFrame,
        train_pct: float = 0.7,
        validation_pct: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        n = len(data)
        train_end = int(n * train_pct)
        val_end = int(n * (train_pct + validation_pct))
        
        train = data.iloc[:train_end].copy()
        validation = data.iloc[train_end:val_end].copy()
        test = data.iloc[val_end:].copy()
        
        logger.info(f"Split: Train={len(train)}, Val={len(validation)}, Test={len(test)}")
        return train, validation, test
