import pytest
import pandas as pd
from technical_indicators import TechnicalIndicators

class TestTechnicalIndicators:
    def test_add_all_indicators(self, sample_data):
        ti = TechnicalIndicators()
        df = ti.add_all_indicators(sample_data)

        expected_cols = ['sma_20', 'rsi_14', 'macd', 'bb_upper']
        for col in expected_cols:
            assert col in df.columns

        # Check for NaNs (dropna is called at the end of add_all_indicators)
        assert not df.isnull().values.any()

    def test_calculate_returns(self, sample_data):
        ti = TechnicalIndicators()
        df = ti.calculate_returns(sample_data)

        assert 'returns' in df.columns
        assert 'log_returns' in df.columns
