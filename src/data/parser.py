import yfinance as yf
import pandas as pd
import logging
from datetime import date
from typing import Optional, List, Dict
from .storage import DataStorage

logger = logging.getLogger(__name__)

class FinancialParser:
    """
    Fetches and parses financial statements (Income, Balance Sheet, Cash Flow).
    """
    
    def __init__(self, use_db: bool = True):
        self.db = DataStorage() if use_db else None
        
    def fetch_and_save_financials(self, ticker: str) -> bool:
        """
        Fetches financials from yfinance, parses them, and saves to DB.
        Returns True if successful.
        """
        try:
            logger.info(f"Fetching financials for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # yfinance returns DataFrame with columns as Dates
            # Rows are metrics (e.g. "Total Revenue")
            
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            # cash_flow = stock.cashflow  # Not using yet but available
            
            if income_stmt.empty or balance_sheet.empty:
                logger.warning(f"No financials found for {ticker}")
                return False
                
            # We need to transpose/merge to get per-date records
            # Common dates are usually columns
            
            # Extract common dates
            dates = income_stmt.columns
            
            parsed_data = []
            
            for d in dates:
                # Convert Timestamp to date
                report_date = d.date() if isinstance(d, pd.Timestamp) else d
                period_str = f"{report_date.year}-FY" # Assuming annual for now
                
                # Helper to safely get value from DF
                def get_val(df, row_name, col_date):
                    try:
                        if row_name in df.index:
                            val = df.loc[row_name, col_date]
                            return float(val) if not pd.isna(val) else None
                    except:
                        return None
                    return None

                # Mapping yfinance row names to our schema
                # Note: yfinance row names can change, need robust matching in future
                revenue = get_val(income_stmt, "Total Revenue", d)
                net_income = get_val(income_stmt, "Net Income", d)
                eps = get_val(income_stmt, "Basic EPS", d) # Sometimes "Basic EPS"
                
                total_assets = get_val(balance_sheet, "Total Assets", d)
                total_liab = get_val(balance_sheet, "Total Liabilities Net Minority Interest", d) 
                # "Total Liabilities Net Minority Interest" is common in yfinance for "Total Liabilities"
                
                record = {
                    'ticker': ticker,
                    'period': period_str,
                    'report_date': report_date,
                    'revenue': revenue,
                    'net_income': net_income,
                    'eps': eps,
                    'total_assets': total_assets,
                    'total_liabilities': total_liab
                }
                parsed_data.append(record)
                
            if self.db:
                self.db.save_financials(ticker, parsed_data)
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing financials for {ticker}: {e}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = FinancialParser()
    parser.fetch_and_save_financials("AAPL")
