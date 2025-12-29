"""
TECHNICAL INDICATORS
====================
Comprehensive technical analysis indicators using TA-Lib.
"""

import pandas as pd
import numpy as np
import talib
from typing import Optional


class TechnicalIndicators:
    """Calculate technical indicators for trading strategies."""
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        result = df.copy()
        
        # Ensure correct data types for TA-Lib
        close = result['close'].astype(np.float64).values
        high = result['high'].astype(np.float64).values
        low = result['low'].astype(np.float64).values
        open_price = result['open'].astype(np.float64).values
        volume = result['volume'].astype(np.float64).values  # TA-Lib wants float64
        
        # Moving Averages
        result['sma_20'] = talib.SMA(close, timeperiod=20)
        result['sma_50'] = talib.SMA(close, timeperiod=50)
        result['sma_200'] = talib.SMA(close, timeperiod=200)
        result['ema_12'] = talib.EMA(close, timeperiod=12)
        result['ema_26'] = talib.EMA(close, timeperiod=26)
        
        # RSI
        result['rsi_14'] = talib.RSI(close, timeperiod=14)
        
        # MACD
        macd, signal, hist = talib.MACD(close)
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_hist'] = hist
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close, timeperiod=20)
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        result['bb_width'] = (upper - lower) / middle
        
        # ATR (Average True Range)
        result['atr_14'] = talib.ATR(high, low, close, timeperiod=14)
        
        # Stochastic
        slowk, slowd = talib.STOCH(high, low, close)
        result['stoch_k'] = slowk
        result['stoch_d'] = slowd
        
        # Volume indicators (OBV wants float64 volume)
        result['obv'] = talib.OBV(close, volume)
        
        # ADX (Trend Strength)
        result['adx_14'] = talib.ADX(high, low, close, timeperiod=14)
        
        # CCI (Commodity Channel Index)
        result['cci_14'] = talib.CCI(high, low, close, timeperiod=14)
        
        return result.dropna()
        
    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Add return calculations."""
        result = df.copy()
        result['returns'] = result['close'].pct_change()
        result['log_returns'] = np.log(result['close'] / result['close'].shift(1))
        return result


if __name__ == "__main__":
    from data_manager import DataManager
    
    dm = DataManager()
    data = dm.fetch_stock_data('AAPL', '2023-01-01', '2023-12-31')
    
    ti = TechnicalIndicators()
    data_with_indicators = ti.add_all_indicators(data)
    
    print("=" * 60)
    print("TECHNICAL INDICATORS TEST")
    print("=" * 60)
    print(f"\nOriginal columns: {list(data.columns)}")
    print(f"\nWith indicators: {list(data_with_indicators.columns)}")
    print(f"\nShape: {data_with_indicators.shape}")
    print("\nSample data:")
    print(data_with_indicators[['close', 'sma_20', 'rsi_14', 'macd']].tail())
