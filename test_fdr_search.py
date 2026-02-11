import FinanceDataReader as fdr
import pandas as pd
import warnings

# 경고 무시 (판다스 버전 등에 따른 경고)
warnings.filterwarnings('ignore')

def test_fdr_search():
    print("Loading KRX data from FinanceDataReader...")
    try:
        # KRX 전체 상장 종목 (주식, ETF 모두 포함)
        df_krx = fdr.StockListing('KRX')
        print(f"Loaded {len(df_krx)} symbols from KRX.")
        print("Columns:", df_krx.columns.tolist())
        
        # 'Code' 혹은 'Symbol' 중 하나를 Symbol로 통일
        symbol_col = 'Code' if 'Code' in df_krx.columns else 'Symbol'
        name_col = 'Name'
        print(f"Using Symbol: {symbol_col}, Name: {name_col}")
        
        # 검색 테스트
        queries = ["TIGER 반도체 TOP10", "TIGER 반도체", "삼성전자", "현대차"]
        
        for q in queries:
            print(f"\nSearching for: {q}")
            
            mask = df_krx[name_col].astype(str).str.contains(q, case=False) | df_krx[symbol_col].astype(str).str.contains(q, case=False)
            results = df_krx[mask]
            
            if not results.empty:
                count = len(results)
                print(f"Found {count} matches.")
                print(results[[symbol_col, name_col]].head(5).to_string(index=False))
            else:
                print("No matches found.")
                
    except Exception as e:
        print(f"Error loading KRX listed: {e}")

if __name__ == "__main__":
    test_fdr_search()
