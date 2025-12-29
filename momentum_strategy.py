"""
MOMENTUM STRATEGY
=================
RSI-based momentum trading.
"""

import pandas as pd
import numpy as np
from strategy_base import StrategyBase


class MomentumStrategy(StrategyBase):
    """RSI momentum strategy."""
    
    def __init__(self, rsi_period: int = 14, threshold: int = 50):
        super().__init__(name="Momentum")
        self.rsi_period = rsi_period
        self.threshold = threshold
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['signal'] = 0
        result['rsi_prev'] = result['rsi_14'].shift(1)
        
        # Buy: RSI crosses above 50
        result.loc[
            (result['rsi_14'] > self.threshold) & 
            (result['rsi_prev'] <= self.threshold),
            'signal'
        ] = 1
        
        # Sell: RSI crosses below 50
        result.loc[
            (result['rsi_14'] < self.threshold) & 
            (result['rsi_prev'] >= self.threshold),
            'signal'
        ] = -1
        
        return result
