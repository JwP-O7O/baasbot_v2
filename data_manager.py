"""
DATA MANAGER - Improved synthetic data with Caching
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import os
import time
from utils.logger import setup_logging
from config.settings import settings

logger = setup_logging(__name__)

class DataManager:
    def __init__(self):
        self.data_dir = settings.get('data.data_dir', './data')
        self.cache_expiry_days = settings.get('data.cache_expiry_days', 1)
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_cache_path(self, symbol: str, start_date: str, end_date: str, interval: str) -> str:
        """Generate a filename for the cache."""
        filename = f"{symbol}_{start_date}_{end_date}_{interval}.parquet"
        return os.path.join(self.data_dir, filename)

    def _is_cache_valid(self, filepath: str) -> bool:
        """Check if cache file exists and is recent."""
        if not os.path.exists(filepath):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        age = datetime.now() - file_time
        return age.days < self.cache_expiry_days

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
        if n > 4:
            regime_length = n // 4  # 4 regimes over period
        else:
            regime_length = n

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
        use_synthetic_on_fail: bool = True,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """Download with improved synthetic fallback and caching."""
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        cache_path = self._get_cache_path(symbol, start_date, end_date, interval)

        if not force_refresh and self._is_cache_valid(cache_path):
            try:
                df = pd.read_parquet(cache_path)
                logger.info(f"✅ Loaded {len(df)} bars from cache for {symbol}")
                return df
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")

        # Try yfinance
        for attempt in range(3):
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, interval=interval)
                
                if not df.empty:
                    df.columns = [col.lower() for col in df.columns]
                    df = df.ffill(limit=3).dropna()

                    # Save to cache
                    try:
                        df.to_parquet(cache_path)
                        logger.info(f"Saved {symbol} to cache.")
                    except Exception as e:
                        logger.warning(f"Failed to save cache: {e}")

                    logger.info(f"✅ Downloaded {len(df)} bars from Yahoo Finance")
                    return df
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(2)
        
        # Fallback to REALISTIC synthetic
        if use_synthetic_on_fail:
            logger.warning(f"Using REALISTIC synthetic data for {symbol}")
            df = self._generate_realistic_synthetic_data(symbol, start_date, end_date)

            # Save synthetic data to cache as well, to simulate persistent data
            try:
                df.to_parquet(cache_path)
                logger.info(f"Saved synthetic {symbol} to cache.")
            except Exception as e:
                logger.warning(f"Failed to save synthetic cache: {e}")

            return df
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
