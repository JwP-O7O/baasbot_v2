"""
TREND FOLLOWING STRATEGY
========================
Follow the trend using moving average crossovers.
"""

import pandas as pd
import numpy as np
from strategy_base import StrategyBase


class TrendFollowingStrategy(StrategyBase):
    """Moving average crossover strategy."""
    
    def __init__(self, fast_period: int = 50, slow_period: int = 200):
        super().__init__(name="Trend Following")
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['signal'] = 0
        
        # Golden cross
        result.loc[
            result[f'sma_{self.fast_period}'] > result[f'sma_{self.slow_period}'],
            'signal'
        ] = 1
        
        # Death cross
        result.loc[
            result[f'sma_{self.fast_period}'] < result[f'sma_{self.slow_period}'],
            'signal'
        ] = -1
        
        return result
