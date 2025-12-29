"""
PAPER TRADING SETUP
===================
Connect to Alpaca paper trading account.
"""

import os
from dotenv import load_dotenv


class AlpacaPaperTrader:
    """Setup Alpaca paper trading."""
    
    def __init__(self):
        self.setup_complete = False
        
    def create_env_template(self):
        """Create .env template for API keys."""
        template = """# ALPACA API CREDENTIALS
# Get these from: https://alpaca.markets (Paper Trading)

ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
"""
        
        with open('.env.example', 'w') as f:
            f.write(template)
        
        print("✅ Created .env.example")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("=" * 60)
        print("1. Go to https://alpaca.markets")
        print("2. Sign up for free account")
        print("3. Go to 'Paper Trading' section")
        print("4. Generate API keys")
        print("5. Copy .env.example to .env")
        print("6. Paste your keys in .env")
        print("=" * 60)
        
    def verify_connection(self):
        """Test connection to Alpaca."""
        load_dotenv()
        
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or api_key == 'your_api_key_here':
            print("❌ API keys not configured")
            print("   Please edit .env file with your Alpaca keys")
            return False
            
        try:
            import alpaca_trade_api as tradeapi
            
            api = tradeapi.REST(
                key_id=api_key,
                secret_key=secret_key,
                base_url='https://paper-api.alpaca.markets'
            )
            
            account = api.get_account()
            
            print("✅ Connected to Alpaca Paper Trading!")
            print(f"\n📊 Account Info:")
            print(f"  Status: {account.status}")
            print(f"  Cash: ${float(account.cash):,.2f}")
            print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
            
            self.setup_complete = True
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 BAASBOT PAPER TRADING SETUP")
    print("=" * 60)
    
    trader = AlpacaPaperTrader()
    
    # Create template
    trader.create_env_template()
    
    print("\n⏸️  PAUSE: Complete setup steps above, then run:")
    print("   python3 paper_trading_setup.py")
    print("\n   (After you've created .env with your keys)")
