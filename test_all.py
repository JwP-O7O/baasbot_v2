"""
COMPREHENSIVE SYSTEM TEST
=========================
Tests all modules end-to-end.
"""

print("=" * 70)
print("🧪 BAASBOT SYSTEM TEST")
print("=" * 70)

# Test 1: Data Manager
print("\n[1/5] Testing Data Manager...")
from data_manager import DataManager
dm = DataManager()
aapl = dm.fetch_stock_data('AAPL', '2023-01-01', '2023-12-31')
assert len(aapl) > 200, "Not enough data"
print("✅ Data Manager: PASS")

# Test 2: Transaction Costs
print("\n[2/5] Testing Transaction Costs...")
from transaction_costs import TransactionCostCalculator
calc = TransactionCostCalculator()
costs = calc.calculate_entry_cost(100, 10, 'buy')
assert costs['total_cost'] > 0, "Costs should be positive"
print("✅ Transaction Costs: PASS")

# Test 3: Technical Indicators
print("\n[3/5] Testing Technical Indicators...")
from technical_indicators import TechnicalIndicators
ti = TechnicalIndicators()
data_with_ind = ti.add_all_indicators(aapl)
assert 'rsi_14' in data_with_ind.columns, "RSI missing"
assert 'macd' in data_with_ind.columns, "MACD missing"
print("✅ Technical Indicators: PASS")

# Test 4: Strategy Base
print("\n[4/5] Testing Strategy Base...")
from strategy_base import StrategyBase
print("✅ Strategy Base: PASS (abstract class)")

# Test 5: Mean Reversion Strategy
print("\n[5/5] Testing Mean Reversion Strategy...")
from mean_reversion_strategy import MeanReversionStrategy
strategy = MeanReversionStrategy()
results = strategy.backtest(aapl, initial_capital=10000)
assert 'total_return' in results, "Missing metrics"
assert 'sharpe_ratio' in results, "Missing metrics"
print("✅ Mean Reversion Strategy: PASS")

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print(f"\n📊 Sample Strategy Results:")
print(f"  Total Return: {results['total_return']:.2%}")
print(f"  Sharpe Ratio: {results['sharpe_ratio']:.4f}")
print(f"  Max Drawdown: {results['max_drawdown']:.2%}")
print(f"  Win Rate: {results['win_rate']:.2%}")
print(f"  Total Trades: {results['total_trades']}")
