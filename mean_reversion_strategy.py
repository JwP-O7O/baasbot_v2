"""
MEAN REVERSION STRATEGY
========================
Buy when RSI oversold, sell when RSI overbought.

Academic basis: Jegadeesh & Titman (1993) - short-term reversals
"""

import pandas as pd
import numpy as np
from strategy_base import StrategyBase


class MeanReversionStrategy(StrategyBase):
    """
    Simple mean reversion using RSI.
    
    Rules:
    - BUY when RSI < 30 (oversold)
    - SELL when RSI > 70 (overbought)
    - HOLD otherwise
    """
    
    def __init__(
        self,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70
    ):
        super().__init__(name="Mean Reversion")
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on RSI."""
        result = data.copy()
        
        # Initialize signal column
        result['signal'] = 0
        
        # BUY signal: RSI < 30
        result.loc[result['rsi_14'] < self.rsi_oversold, 'signal'] = 1
        
        # SELL signal: RSI > 70
        result.loc[result['rsi_14'] > self.rsi_overbought, 'signal'] = -1
        
        return result


if __name__ == "__main__":
    from data_manager import DataManager
    
    print("=" * 60)
    print("MEAN REVERSION STRATEGY TEST")
    print("=" * 60)
    
    # Load data
    dm = DataManager()
    data = dm.fetch_stock_data('AAPL', '2020-01-01', '2023-12-31')
    
    # Initialize strategy
    strategy = MeanReversionStrategy()
    
    # Run backtest
    results = strategy.backtest(data, initial_capital=10000)
    
    print(f"\n📊 Results for {strategy.name}:")
    print(f"  Total Return: {results['total_return']:.2%}")
    print(f"  Sharpe Ratio: {results['sharpe_ratio']:.4f}")
    print(f"  Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"  Win Rate: {results['win_rate']:.2%}")
    print(f"  Total Trades: {results['total_trades']}")
    
    print("\n✅ Strategy test complete!")
