import pytest
import pandas as pd
import numpy as np
import os
import shutil
from config.settings import settings

@pytest.fixture(scope="session")
def test_config():
    """Setup test configuration."""
    # Ensure we use a test data directory
    test_data_dir = "./test_data"
    os.makedirs(test_data_dir, exist_ok=True)

    # We can't easily mock the singleton settings without some hackery,
    # but we can modify the config dict if needed, or rely on file IO mocking.
    # For now, we will rely on checking that the code uses the values.

    yield

    # Cleanup
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

@pytest.fixture
def sample_data():
    """Generate synthetic OHLCV data for testing."""
    # Increased to 400 to ensure enough data for long-period indicators (e.g. SMA 200)
    # and subsequent operations that might drop NaNs
    periods = 400
    dates = pd.date_range(start="2023-01-01", periods=periods, freq="D")

    # Generate somewhat realistic random walk to avoid weird indicator behaviors
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, periods)
    price_path = 100 * (1 + returns).cumprod()

    df = pd.DataFrame({
        'open': price_path,
        'high': price_path * 1.02,
        'low': price_path * 0.98,
        'close': price_path,
        'volume': np.random.randint(1000, 10000, periods)
    }, index=dates)

    return df
