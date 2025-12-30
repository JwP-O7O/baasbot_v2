import pytest
import os
import pandas as pd
from data_manager import DataManager
from unittest.mock import MagicMock, patch

class TestDataManager:
    def test_init(self):
        dm = DataManager()
        assert os.path.exists(dm.data_dir)

    def test_synthetic_data_generation(self):
        dm = DataManager()
        df = dm._generate_realistic_synthetic_data('TEST', '2023-01-01', '2023-02-01')
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])

    @patch('data_manager.yf.Ticker')
    def test_fetch_stock_data_yfinance(self, mock_ticker):
        # Setup mock
        mock_instance = MagicMock()
        mock_ticker.return_value = mock_instance

        # Create dummy data
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        mock_df = pd.DataFrame({
            'Open': [100]*10, 'High': [110]*10, 'Low': [90]*10, 'Close': [105]*10, 'Volume': [1000]*10
        }, index=dates)
        mock_instance.history.return_value = mock_df

        dm = DataManager()
        df = dm.fetch_stock_data('AAPL', '2023-01-01', '2023-01-10', force_refresh=True)

        assert not df.empty
        assert len(df) == 10
        # Columns should be lowercased
        assert 'close' in df.columns

    def test_caching(self, tmp_path):
        # Override data_dir for this test
        dm = DataManager()
        dm.data_dir = str(tmp_path)

        symbol = 'CACHE_TEST'
        start = '2023-01-01'
        end = '2023-01-10'
        interval = '1d'

        # 1. Generate data (will use synthetic)
        df1 = dm.fetch_stock_data(symbol, start, end, interval, use_synthetic_on_fail=True)

        # 2. Check if file exists
        cache_path = dm._get_cache_path(symbol, start, end, interval)
        assert os.path.exists(cache_path)

        # 3. Fetch again (should load from cache)
        # We modify the file timestamp to ensure it's considered valid if we had stricter checks,
        # but here we mainly check if it reads the file.
        # To verify it's reading cache, we can modify the cache file content manually.

        df_cached = pd.read_parquet(cache_path)
        df_cached['close'] = 9999.0 # Modify cache
        df_cached.to_parquet(cache_path)

        df2 = dm.fetch_stock_data(symbol, start, end, interval)
        assert df2['close'].iloc[0] == 9999.0
