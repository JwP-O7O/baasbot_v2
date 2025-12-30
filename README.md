# Trading Bot

This is an automated trading bot framework supporting multiple strategies, backtesting, and paper trading via Alpaca.

## Structure

- `config/`: Configuration files and settings manager.
- `utils/`: Utility functions (logging, etc.).
- `data/`: Data storage and cache.
- `tests/`: Unit tests.
- `*.py`: Core logic files.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the bot:
   - Edit `config/config.yaml` to adjust strategy parameters, logging settings, etc.
   - For paper trading, copy `.env.example` to `.env` and add your Alpaca API keys.

## Running Tests

Run the full test suite with:

```bash
pytest
```

## Strategies

- **Momentum**: RSI-based trend following.
- **Mean Reversion**: RSI-based mean reversion.

Strategies are defined in `momentum_strategy.py`, `mean_reversion_strategy.py`, etc., and inherit from `StrategyBase`.
