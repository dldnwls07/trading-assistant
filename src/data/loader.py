import logging
import pandas as pd
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class KRXLoader:
    """
    Responsibilities:
    - Load KRX stock listing data using FinanceDataReader.
    - Provide search functionality for ticker mapping.
    - Cache data in memory to prevent repeated network calls.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KRXLoader, cls).__new__(cls)
            cls._instance.df = None
            cls._instance.loading = False
        return cls._instance

    def load(self):
        """Loads KRX data into memory (thread-safe logic handled by caller if needed)"""
        if self.loading or self.df is not None: 
            return
        
        self.loading = True
        try:
            import FinanceDataReader as fdr
            logger.info("📦 Loading KRX data from FinanceDataReader...")
            self.df = fdr.StockListing('KRX')
            logger.info(f"✅ Loaded {len(self.df)} KRX symbols.")
        except Exception as e:
            logger.error(f"❌ Failed to load KRX data: {e}")
        finally:
            self.loading = False

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for stocks by Name or Code.
        Returns a list of candidate dictionaries.
        """
        if self.df is None: 
            return []
            
        try:
            q = query.strip()
            # Search in Name or Code columns
            mask = self.df['Name'].astype(str).str.contains(q, case=False, na=False) | \
                   self.df['Code'].astype(str).str.contains(q, case=False, na=False)
            
            results = self.df[mask].head(limit)
            
            candidates = []
            for _, row in results.iterrows():
                market = row.get('Market', 'KRX')
                code = str(row.get('Code', ''))
                name = row.get('Name', '')
                
                # Determine suffix based on Market
                suffix = ".KS" if market in ['KOSPI', 'KOSPI200'] else ".KQ"
                
                # Standardize Symbol: 6-digit code -> append suffix
                # Some ETF/ETN might differ, but this covers most logic
                symbol = f"{code}{suffix}" if code.isdigit() and len(code) == 6 else code
                
                candidates.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": market,
                    "is_korean": True
                })
            return candidates
        except Exception as e:
            logger.error(f"❌ KRX Search error: {e}")
            return []

# Singleton Global Accessor
krx_loader = KRXLoader()
