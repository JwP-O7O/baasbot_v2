"""
STRATEGY BASE CLASS
===================
Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from technical_indicators import TechnicalIndicators
from config.settings import settings


class StrategyBase(ABC):
    """Base class that all strategies must inherit from."""
    
    def __init__(self, name: str):
        self.name = name
        self.ti = TechnicalIndicators()
        self.config = settings.get(f'strategies.{name}', {})
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals.
        
        Args:
            data: DataFrame with OHLCV + indicators
            
        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        pass
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add indicators to raw OHLCV data."""
        data_with_indicators = self.ti.add_all_indicators(data)
        data_with_indicators = self.ti.calculate_returns(data_with_indicators)
        return data_with_indicators
        
    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert signals to positions.
        
        Signal logic:
        - 1 (buy signal) → position = 1 (long)
        - -1 (sell signal) → position = 0 (flat)
        - 0 (hold) → maintain previous position
        """
        result = signals.copy()
        result['position'] = result['signal'].replace(0, np.nan).ffill().fillna(0)
        return result
        
    def backtest(
        self, 
        data: pd.DataFrame,
        initial_capital: float = 10000
    ) -> Dict[str, float]:
        """
        Run backtest and calculate performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        # Prepare data
        prepared = self.prepare_data(data)
        
        # Generate signals
        with_signals = self.generate_signals(prepared)
        
        # Calculate positions
        with_positions = self.calculate_positions(with_signals)
        
        # Calculate returns
        with_positions['strategy_returns'] = (
            with_positions['position'].shift(1) * with_positions['returns']
        )
        
        # Calculate equity curve
        with_positions['equity'] = initial_capital * (
            1 + with_positions['strategy_returns']
        ).cumprod()
        
        # Performance metrics
        total_return = (with_positions['equity'].iloc[-1] / initial_capital) - 1
        
        returns = with_positions['strategy_returns'].dropna()
        sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Max drawdown
        equity = with_positions['equity']
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_dd = drawdown.min()
        
        # Win rate
        winning_trades = (with_positions['strategy_returns'] > 0).sum()
        total_trades = (with_positions['strategy_returns'] != 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'equity_curve': with_positions['equity']
        }


if __name__ == "__main__":
    print("✅ Strategy base class defined")
    print("This is an abstract class - use specific strategies like MeanReversionStrategy")
