import pytest
import pandas as pd
from momentum_strategy import MomentumStrategy
from mean_reversion_strategy import MeanReversionStrategy

class TestStrategies:
    def test_momentum_strategy(self, sample_data):
        strategy = MomentumStrategy()
        # Ensure config is loaded
        assert strategy.name == "momentum"
        assert strategy.threshold == 50 # Default from config/class

        # We need to add indicators first because strategy expects them
        # But StrategyBase.backtest calls prepare_data which adds indicators.
        # So we can test backtest directly or prepare_data + generate_signals.

        results = strategy.backtest(sample_data, initial_capital=10000)

        assert 'total_return' in results
        assert 'sharpe_ratio' in results
        assert isinstance(results['equity_curve'], pd.Series)

    def test_mean_reversion_strategy(self, sample_data):
        strategy = MeanReversionStrategy()
        assert strategy.name == "mean_reversion"

        results = strategy.backtest(sample_data, initial_capital=10000)

        assert 'total_return' in results
        assert 'win_rate' in results
