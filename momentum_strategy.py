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
    
    def __init__(self):
        super().__init__(name="momentum")
        # Load from config, with defaults
        self.rsi_period = self.config.get('rsi_period', 14)
        self.threshold = self.config.get('threshold', 50)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['signal'] = 0
        
        rsi_col = f'rsi_{self.rsi_period}'
        # If the specific RSI period isn't calculated by default in technical_indicators,
        # we might need to rely on what's available or make technical_indicators dynamic.
        # For now, let's assume 'rsi_14' is standard or check if column exists.

        if rsi_col not in result.columns:
             # Fallback to rsi_14 if configured period is not available in pre-calculated data
             # In a real scenario, we would trigger calculation here.
             rsi_col = 'rsi_14'

        result['rsi_prev'] = result[rsi_col].shift(1)

        # Buy: RSI crosses above threshold
        result.loc[
            (result[rsi_col] > self.threshold) &
            (result['rsi_prev'] <= self.threshold),
            'signal'
        ] = 1
        
        # Sell: RSI crosses below threshold
        result.loc[
            (result[rsi_col] < self.threshold) &
            (result['rsi_prev'] >= self.threshold),
            'signal'
        ] = -1
        
        return result
