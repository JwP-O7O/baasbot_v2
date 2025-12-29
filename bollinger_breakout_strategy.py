"""
BOLLINGER BREAKOUT STRATEGY
============================
Trade breakouts from Bollinger Bands.
"""

import pandas as pd
import numpy as np
from strategy_base import StrategyBase


class BollingerBreakoutStrategy(StrategyBase):
    """Bollinger Band breakout strategy."""
    
    def __init__(self):
        super().__init__(name="Bollinger Breakout")
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['signal'] = 0
        
        # Buy: Close above upper band
        result.loc[result['close'] > result['bb_upper'], 'signal'] = 1
        
        # Sell: Close below lower band
        result.loc[result['close'] < result['bb_lower'], 'signal'] = -1
        
        return result
