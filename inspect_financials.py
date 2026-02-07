import yfinance as yf
import pandas as pd

def inspect():
    ticker = "AAPL"
    stock = yf.Ticker(ticker)
    
    print("--- Income Statement Index ---")
    print(stock.financials.index.tolist())
    
    print("\n--- Balance Sheet Index ---")
    print(stock.balance_sheet.index.tolist())

if __name__ == "__main__":
    inspect()
