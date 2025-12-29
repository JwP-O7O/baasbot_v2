"""
TRANSACTION COST MODEL
======================
Realistic cost modeling for backtesting.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class CostModel:
    """Transaction cost configuration."""
    commission_pct: float = 0.0      # 0% for Alpaca
    commission_min: float = 0.0      # $0 minimum
    spread_pct: float = 0.01         # 0.01% = 1 bps
    slippage_pct: float = 0.05       # 0.05% = 5 bps
    market_impact: float = 0.0       # For future use


class TransactionCostCalculator:
    """Calculate realistic transaction costs."""
    
    def __init__(self, cost_model: CostModel = None):
        self.model = cost_model or CostModel()
        
    def calculate_entry_cost(
        self,
        price: float,
        quantity: float,
        side: str = "buy"
    ) -> Dict[str, float]:
        """
        Calculate cost to enter a position.
        
        Returns:
            Dictionary with cost breakdown
        """
        gross_value = price * quantity
        
        # Commission
        commission = max(
            gross_value * self.model.commission_pct / 100,
            self.model.commission_min
        )
        
        # Spread cost
        spread_cost = gross_value * self.model.spread_pct / 100
        
        # Slippage
        slippage_cost = gross_value * self.model.slippage_pct / 100
        
        total_cost = commission + spread_cost + slippage_cost
        
        if side == "buy":
            effective_price = (gross_value + total_cost) / quantity
        else:
            effective_price = (gross_value - total_cost) / quantity
            
        return {
            'gross_value': gross_value,
            'commission': commission,
            'spread_cost': spread_cost,
            'slippage_cost': slippage_cost,
            'total_cost': total_cost,
            'effective_price': effective_price
        }
        
    def calculate_roundtrip_cost(
        self,
        entry_price: float,
        exit_price: float,
        quantity: float
    ) -> float:
        """Calculate total cost for complete trade (buy + sell)."""
        entry = self.calculate_entry_cost(entry_price, quantity, 'buy')
        exit = self.calculate_entry_cost(exit_price, quantity, 'sell')
        return entry['total_cost'] + exit['total_cost']


if __name__ == "__main__":
    calc = TransactionCostCalculator()
    
    print("=" * 60)
    print("TRANSACTION COST EXAMPLES")
    print("=" * 60)
    
    # Example: $1000 trade
    costs = calc.calculate_entry_cost(price=100, quantity=10, side='buy')
    print(f"\nBuy 10 shares @ $100:")
    print(f"  Total cost: ${costs['total_cost']:.2f}")
    print(f"  Effective price: ${costs['effective_price']:.4f}")
    
    # Roundtrip
    roundtrip = calc.calculate_roundtrip_cost(100, 101, 10)
    print(f"\nRoundtrip cost (buy $100, sell $101): ${roundtrip:.2f}")
    print(f"Break-even price move needed: {(roundtrip/1000)*100:.2f}%")
