"""
LIVE PAPER TRADER
=================
Execute strategies in real-time on Alpaca paper account.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd

from data_manager import DataManager
from momentum_strategy import MomentumStrategy
from mean_reversion_strategy import MeanReversionStrategy
from trend_following_strategy import TrendFollowingStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class LivePaperTrader:
    """Execute strategies on Alpaca paper account."""
    
    def __init__(self, strategy, symbols=['AAPL'], check_interval=300):
        """
        Args:
            strategy: TradingStrategy instance
            symbols: List of symbols to trade
            check_interval: Seconds between checks (300 = 5 minutes)
        """
        load_dotenv()
        
        self.api = tradeapi.REST(
            key_id=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY'),
            base_url=os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        )
        
        self.strategy = strategy
        self.symbols = symbols
        self.check_interval = check_interval
        self.dm = DataManager()
        
        self.positions = {}
        self.trade_log = []
        
    def get_account_info(self):
        """Get current account status."""
        account = self.api.get_account()
        return {
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power),
            'equity': float(account.equity)
        }
        
    def get_current_position(self, symbol):
        """Get current position for symbol."""
        try:
            position = self.api.get_position(symbol)
            return {
                'qty': int(position.qty),
                'avg_entry': float(position.avg_entry_price),
                'market_value': float(position.market_value),
                'unrealized_pl': float(position.unrealized_pl)
            }
        except:
            return None
            
    def place_order(self, symbol, qty, side):
        """Place market order."""
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day'
            )
            logger.info(f"✅ {side.upper()} order placed: {qty} {symbol}")
            return order
        except Exception as e:
            logger.error(f"❌ Order failed: {str(e)}")
            return None
            
    def execute_trading_cycle(self):
        """Execute one trading cycle for all symbols."""
        account = self.get_account_info()
        logger.info(f"💰 Portfolio Value: ${account['portfolio_value']:,.2f}")
        
        for symbol in self.symbols:
            try:
                # Get recent data (6 months for indicators)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=180)
                
                data = self.dm.fetch_stock_data(
                    symbol,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                # Get strategy signal
                prepared = self.strategy.prepare_data(data)
                with_signals = self.strategy.generate_signals(prepared)
                
                latest_signal = with_signals['signal'].iloc[-1]
                latest_price = with_signals['close'].iloc[-1]
                
                # Get current position
                current_pos = self.get_current_position(symbol)
                
                # Execute logic
                if latest_signal == 1 and current_pos is None:
                    # BUY signal and no position
                    cash = account['cash']
                    qty = int(cash * 0.2 / latest_price)  # Use 20% of cash
                    
                    if qty > 0:
                        self.place_order(symbol, qty, 'buy')
                        logger.info(f"📈 {symbol} BUY signal @ ${latest_price:.2f}")
                        
                elif latest_signal == -1 and current_pos is not None:
                    # SELL signal and have position
                    qty = abs(current_pos['qty'])
                    self.place_order(symbol, qty, 'sell')
                    logger.info(f"📉 {symbol} SELL signal @ ${latest_price:.2f}")
                    
                    # Log P&L
                    pnl = current_pos['unrealized_pl']
                    logger.info(f"💵 Realized P&L: ${pnl:.2f}")
                    
                else:
                    status = "LONG" if current_pos else "FLAT"
                    logger.info(f"⏸️  {symbol} HOLD ({status}) @ ${latest_price:.2f}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {str(e)}")
                
    def run(self, duration_hours=None):
        """
        Run live trading loop.
        
        Args:
            duration_hours: Run for X hours (None = infinite)
        """
        logger.info("=" * 60)
        logger.info(f"🤖 LIVE PAPER TRADER STARTED")
        logger.info(f"Strategy: {self.strategy.name}")
        logger.info(f"Symbols: {', '.join(self.symbols)}")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            while True:
                # Check market hours (Alpaca paper trades 24/5 but we follow real market)
                now = datetime.now()
                if now.weekday() < 5:  # Monday-Friday
                    self.execute_trading_cycle()
                else:
                    logger.info("📅 Weekend - Market closed")
                
                # Check duration limit
                if duration_hours:
                    elapsed = (datetime.now() - start_time).total_seconds() / 3600
                    if elapsed >= duration_hours:
                        logger.info(f"⏱️  Duration limit reached ({duration_hours}h)")
                        break
                
                # Sleep until next check
                logger.info(f"💤 Sleeping {self.check_interval}s...\n")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopped by user")
            
        finally:
            # Final summary
            account = self.get_account_info()
            logger.info("\n" + "=" * 60)
            logger.info("📊 FINAL SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
            logger.info(f"Cash: ${account['cash']:,.2f}")


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 BAASBOT LIVE PAPER TRADER")
    print("=" * 60)
    
    # Check if API keys configured
    load_dotenv()
    if not os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_API_KEY') == 'your_api_key_here':
        print("\n❌ Alpaca API keys not configured!")
        print("1. Sign up: https://alpaca.markets")
        print("2. Get paper trading keys")
        print("3. Create .env file with keys")
        print("4. Run: python3 paper_trading_setup.py")
        exit(1)
    
    # Initialize with MOMENTUM (the winner!)
    strategy = MomentumStrategy()
    
    trader = LivePaperTrader(
        strategy=strategy,
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        check_interval=300  # 5 minutes
    )
    
    # Run for 1 hour (test mode)
    print("\n⚠️  TEST MODE: Running for 1 hour")
    print("Press Ctrl+C to stop early\n")
    
    trader.run(duration_hours=1)
