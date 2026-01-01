"""
STRATEGY COMPARISON TOOL
========================
Compare all strategies side-by-side.
"""

import pandas as pd
import numpy as np
from typing import List
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from strategy_base import StrategyBase


class StrategyComparison:
    """Compare multiple trading strategies."""
    
    def __init__(self, strategies: List[StrategyBase]):
        self.strategies = strategies
        self.results = {}
        
    def run_comparison(self, data: pd.DataFrame, initial_capital: float = 10000) -> pd.DataFrame:
        """Run all strategies and compare."""
        comparison_data = []
        
        for strategy in self.strategies:
            print(f"🔄 Testing {strategy.name}...")
            
            try:
                results = strategy.backtest(data, initial_capital)
                self.results[strategy.name] = results
                
                comparison_data.append({
                    'Strategy': strategy.name,
                    'Total Return': results['total_return'],
                    'Sharpe Ratio': results['sharpe_ratio'],
                    'Max Drawdown': results['max_drawdown'],
                    'Win Rate': results['win_rate'],
                    'Total Trades': results['total_trades']
                })
                print(f"  ✅ {strategy.name}: {results['total_return']:.2%} return")
                
            except Exception as e:
                print(f"  ❌ {strategy.name} failed: {str(e)}")
        
        df = pd.DataFrame(comparison_data)
        return df.sort_values('Sharpe Ratio', ascending=False)
        
    def plot_comparison(self, filename='strategy_comparison.png'):
        """Plot equity curves."""
        plt.figure(figsize=(14, 7))
        
        for strategy_name, results in self.results.items():
            equity = results['equity_curve']
            returns = (equity / equity.iloc[0] - 1) * 100  # Percentage
            plt.plot(returns.index, returns.values, label=strategy_name, linewidth=2)
        
        plt.title('Strategy Comparison - Cumulative Returns (%)', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Return (%)', fontsize=12)
        plt.legend(fontsize=10, loc='best')
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n📊 Chart saved: {filename}")
        plt.close()

    def plot_interactive_comparison(self, filename='strategy_comparison.html'):
        """Plot interactive equity curves using Plotly."""
        fig = go.Figure()

        for strategy_name, results in self.results.items():
            equity = results['equity_curve']
            returns = (equity / equity.iloc[0] - 1) * 100

            fig.add_trace(go.Scatter(
                x=returns.index,
                y=returns.values,
                mode='lines',
                name=strategy_name,
                hovertemplate='%{y:.2f}%<extra></extra>'
            ))

        fig.update_layout(
            title='Strategy Comparison - Cumulative Returns (%)',
            xaxis_title='Date',
            yaxis_title='Return (%)',
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)

        fig.write_html(filename)
        print(f"📊 Interactive chart saved: {filename}")


if __name__ == "__main__":
    from data_manager import DataManager
    from mean_reversion_strategy import MeanReversionStrategy
    from trend_following_strategy import TrendFollowingStrategy
    from momentum_strategy import MomentumStrategy
    from macd_strategy import MACDStrategy
    from bollinger_breakout_strategy import BollingerBreakoutStrategy
    
    print("=" * 70)
    print("📊 STRATEGY COMPARISON")
    print("=" * 70)
    
    # Load data
    dm = DataManager()
    data = dm.fetch_stock_data('AAPL', '2022-01-01', '2023-12-31')
    print(f"\n✅ Loaded {len(data)} days of data\n")
    
    # Initialize strategies
    strategies = [
        MeanReversionStrategy(),
        TrendFollowingStrategy(),
        MomentumStrategy(),
        MACDStrategy(),
        BollingerBreakoutStrategy()
    ]
    
    # Run comparison
    comparator = StrategyComparison(strategies)
    comparison = comparator.run_comparison(data)
    
    print("\n" + "=" * 70)
    print("📈 RESULTS SUMMARY (Ranked by Sharpe Ratio)")
    print("=" * 70)
    print(comparison.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    
    # Plot
    comparator.plot_comparison()
    comparator.plot_interactive_comparison()
    
    print("\n✅ Comparison complete!")
