"""
MACD STRATEGY
=============
MACD crossover trading.
"""

import pandas as pd
import numpy as np
from strategy_base import StrategyBase


class MACDStrategy(StrategyBase):
    """MACD crossover strategy."""
    
    def __init__(self):
        super().__init__(name="MACD")
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['signal'] = 0
        result['macd_prev'] = result['macd'].shift(1)
        result['signal_prev'] = result['macd_signal'].shift(1)
        
        # Buy: MACD crosses above signal
        result.loc[
            (result['macd'] > result['macd_signal']) & 
            (result['macd_prev'] <= result['signal_prev']),
            'signal'
        ] = 1
        
        # Sell: MACD crosses below signal
        result.loc[
            (result['macd'] < result['macd_signal']) & 
            (result['macd_prev'] >= result['signal_prev']),
            'signal'
        ] = -1
        
        return result
