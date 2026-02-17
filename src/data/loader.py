import pandas as pd
import logging
from typing import Optional, List, Dict, Any
from src.config import settings

logger = logging.getLogger(__name__)

class KRXLoader:
    """
    KRX 한국거래소 전종목 시세 로딩 클래스
    - 서버 시작 시 1회 로딩하여 메모리에 상주
    - 검색 기능(Autocomplete) 제공
    """
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.is_loaded = False

    def load(self):
        """
        KRX 전체 종목 시세 다운로드 (finance-datareader)
        """
        try:
            import FinanceDataReader as fdr
            logger.info("⏳ Loading KRX data (this may take 10-20 seconds)...")
            
            # KRX 전체 (KOSPI + KOSDAQ + KONEX)
            df_krx = fdr.StockListing('KRX')
            
            # 필요한 컬럼만 선택 및 정리
            if 'Code' in df_krx.columns and 'Name' in df_krx.columns:
                self.df = df_krx[['Code', 'Name', 'Market', 'Sector', 'Industry']].copy()
                self.df['Code'] = self.df['Code'].astype(str)
                # 티커 변환 (숫자 -> .KS/.KQ)
                self.df['Symbol'] = self.df.apply(self._convert_to_yfinance, axis=1)
                
                self.is_loaded = True
                logger.info(f"✅ KRX data loaded: {len(self.df)} tickers")
            else:
                logger.warning("KRX data format changed. Check FinanceDataReader.")
                
        except Exception as e:
            logger.error(f"KRX Load Failed: {e}")
            self.is_loaded = False

    def _convert_to_yfinance(self, row) -> str:
        """KOSPI -> .KS, KOSDAQ -> .KQ 변환"""
        code = row['Code']
        market = row['Market']
        
        if market == 'KOSPI':
            return f"{code}.KS"
        elif market == 'KOSDAQ':
            return f"{code}.KQ"
        else:
            return code # KONEX 등은 그대로

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        종목명 또는 코드로 검색
        """
        if not self.is_loaded or self.df is None:
            return []
        
        query = query.upper()
        
        # 1. 코드 검색 (Exact Match 우선)
        code_match = self.df[self.df['Code'] == query]
        
        # 2. 이름 검색 (Contains)
        name_match = self.df[self.df['Name'].str.contains(query, na=False)]
        
        # 병합 (중복 제거)
        results = pd.concat([code_match, name_match]).drop_duplicates().head(limit)
        
        candidates = []
        for _, row in results.iterrows():
            candidates.append({
                "symbol": row['Symbol'],
                "name": row['Name'],
                "exchange": row['Market'],
                "is_korean": True,
                "sector": row.get('Sector', ''),
                "industry": row.get('Industry', '')
            })
            
        return candidates

# 싱글톤 인스턴스
krx_loader = KRXLoader()
