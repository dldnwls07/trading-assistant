import logging
import sys
import os
import io

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.join(os.getcwd(), 'src'))

from data.collector import MarketDataCollector
from data.storage import DataStorage
from data.parser import FinancialParser
from agents.analyst import StockAnalyst

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ticker(ticker):
    print(f"\n{'='*50}")
    print(f"Testing: {ticker}")
    print('='*50)
    
    collector = MarketDataCollector(use_db=True)
    storage = DataStorage("trading_assistant.db")
    parser = FinancialParser(use_db=True)
    analyst = StockAnalyst()
    
    # Fetch data
    print("Fetching price data...")
    price_df = collector.get_daily_ohlcv(ticker, period="1y")
    
    if price_df is None or len(price_df) < 5:
        print(f"Failed to fetch data for {ticker}")
        return
        
    print(f"Got {len(price_df)} price records")
    print(f"Latest price: {price_df['Close'].iloc[-1]:.2f}")
    
    # Fetch financials
    financials = storage.get_financials(ticker)
    if not financials:
        print("Fetching financials...")
        parser.fetch_and_save_financials(ticker)
        financials = storage.get_financials(ticker)
    
    print(f"Got {len(financials) if financials else 0} financial records")
    
    # Analyze
    result = analyst.analyze_ticker(ticker, price_df, financials)
    
    print(f"\n--- Analysis Result ---")
    print(f"Signal: {result['signal']}")
    print(f"Score: {result['final_score']}/100")
    print(f"Technical Score: {result['technical']['score']}")
    print(f"Fundamental Score: {result['fundamental']['score']}")
    
    entry = result.get('entry_points', {})
    if entry:
        print(f"\n--- Entry Points ---")
        print(f"Current Price: {entry.get('current_price', 0):,.2f}")
        print(f"Buy Target 1: {entry.get('buy_target_1', 0):,.2f}")
        print(f"Buy Target 2: {entry.get('buy_target_2', 0):,.2f}")
        print(f"Stop Loss: {entry.get('stop_loss', 0):,.2f}")
        print(f"Sell Target 1: {entry.get('sell_target_1', 0):,.2f}")
        print(f"Sell Target 2: {entry.get('sell_target_2', 0):,.2f}")
    
    print("\n--- Technical Details ---")
    for detail in result['technical'].get('details', [])[:5]:
        # Remove emoji for console
        clean_detail = detail.replace('📈', '[UP]').replace('📉', '[DOWN]').replace('🚀', '[ROCKET]').replace('💡', '[TIP]').replace('⚠️', '[WARN]').replace('✅', '[OK]').replace('🔥', '[FIRE]').replace('❄️', '[COLD]').replace('📍', '[PIN]')
        print(f"  {clean_detail}")

if __name__ == "__main__":
    # Test US Stock
    test_ticker("AAPL")
    
    # Test Korean Stock
    print("\n" + "="*60)
    print("TESTING KOREAN STOCK (Samsung Electronics)")
    print("="*60)
    test_ticker("005930.KS")
