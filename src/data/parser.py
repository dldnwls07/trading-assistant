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
        
    async def fetch_and_save_financials(self, ticker: str) -> bool:
        """
        Fetches financials from yfinance, parses them, and saves to DB.
        Returns True if successful.
        """
        try:
            logger.info(f"Fetching financials for {ticker}...")
            # yfinance는 동기 라이브러리이므로 별도 스레드에서 실행하거나 동기로 유지
            # 여기서는 DB 저장 부분만 비동기로 처리
            stock = yf.Ticker(ticker)
            
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            
            if income_stmt.empty or balance_sheet.empty:
                logger.warning(f"No financials found for {ticker}")
                return False
                
            dates = income_stmt.columns
            parsed_data = []
            
            for d in dates:
                report_date = d.date() if isinstance(d, pd.Timestamp) else d
                period_str = f"{report_date.year}-FY"
                
                def get_val(df, row_name, col_date):
                    try:
                        if row_name in df.index:
                            val = df.loc[row_name, col_date]
                            return float(val) if not pd.isna(val) else None
                    except: return None
                    return None

                revenue = get_val(income_stmt, "Total Revenue", d)
                net_income = get_val(income_stmt, "Net Income", d)
                eps = get_val(income_stmt, "Basic EPS", d)
                total_assets = get_val(balance_sheet, "Total Assets", d)
                total_liab = get_val(balance_sheet, "Total Liabilities Net Minority Interest", d) 
                
                record = {
                    'ticker': ticker, 'period': period_str, 'report_date': report_date,
                    'revenue': revenue, 'net_income': net_income, 'eps': eps,
                    'total_assets': total_assets, 'total_liabilities': total_liab
                }
                parsed_data.append(record)
                
            if self.db:
                await self.db.save_financials(ticker, parsed_data)
                
            return True
        except Exception as e:
            logger.error(f"Error processing financials for {ticker}: {e}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = FinancialParser()
    parser.fetch_and_save_financials("AAPL")
