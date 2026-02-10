"""
FRED API 연동 - 무료 거시 경제 지표
Trading Economics 대체용
"""
import requests
import pandas as pd
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class FREDDataProvider:
    """
    Federal Reserve Economic Data (FRED) API 클라이언트
    무료로 주요 거시 경제 지표 제공
    
    주요 지표:
    - 금리 (Federal Funds Rate)
    - 인플레이션 (CPI)
    - 실업률 (Unemployment Rate)
    - GDP 성장률
    - 10년물 국채 수익률
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    # 주요 경제 지표 시리즈 ID
    SERIES_IDS = {
        "fed_funds_rate": "DFF",  # Federal Funds Effective Rate
        "cpi": "CPIAUCSL",  # Consumer Price Index
        "unemployment": "UNRATE",  # Unemployment Rate
        "gdp": "GDP",  # Gross Domestic Product
        "treasury_10y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
        "treasury_2y": "DGS2",  # 2-Year Treasury
        "vix": "VIXCLS",  # CBOE Volatility Index
        "industrial_production": "INDPRO",  # Industrial Production Index
        "retail_sales": "RSXFS",  # Retail Sales
        "housing_starts": "HOUST"  # Housing Starts
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: FRED API 키 (https://fred.stlouisfed.org/docs/api/api_key.html)
        """
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        
        if not self.api_key:
            logger.warning("FRED_API_KEY가 설정되지 않았습니다. 일부 기능이 제한될 수 있습니다.")
    
    def get_series(self, 
                   series_id: str,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        특정 경제 지표 시계열 데이터 조회
        
        Args:
            series_id: FRED 시리즈 ID (예: "DFF")
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            
        Returns:
            DataFrame with columns: date, value
        """
        if not self.api_key:
            logger.error("API 키가 필요합니다.")
            return None
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/series/observations",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            observations = data.get("observations", [])
            
            if not observations:
                return None
            
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df[['date', 'value']].dropna()
            
            return df
            
        except Exception as e:
            logger.error(f"FRED 데이터 조회 실패 ({series_id}): {e}")
            return None
    
    def get_latest_value(self, series_id: str) -> Optional[float]:
        """최신 값 조회"""
        df = self.get_series(series_id)
        if df is not None and not df.empty:
            return df['value'].iloc[-1]
        return None
    
    def get_macro_snapshot(self) -> Dict[str, Any]:
        """
        주요 거시 경제 지표 스냅샷
        
        Returns:
            {
                "fed_funds_rate": 5.33,
                "cpi_yoy": 3.2,
                "unemployment": 3.8,
                "treasury_10y": 4.5,
                ...
            }
        """
        snapshot = {}
        
        # 1. 연준 기준금리
        fed_rate = self.get_latest_value(self.SERIES_IDS["fed_funds_rate"])
        if fed_rate:
            snapshot["fed_funds_rate"] = round(fed_rate, 2)
        
        # 2. CPI (전년 대비 변화율)
        cpi_df = self.get_series(
            self.SERIES_IDS["cpi"],
            start_date=(datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        )
        if cpi_df is not None and len(cpi_df) >= 12:
            current_cpi = cpi_df['value'].iloc[-1]
            year_ago_cpi = cpi_df['value'].iloc[-13]  # 12개월 전
            cpi_yoy = ((current_cpi - year_ago_cpi) / year_ago_cpi * 100)
            snapshot["cpi_yoy"] = round(cpi_yoy, 2)
        
        # 3. 실업률
        unemployment = self.get_latest_value(self.SERIES_IDS["unemployment"])
        if unemployment:
            snapshot["unemployment_rate"] = round(unemployment, 1)
        
        # 4. 10년물 국채 수익률
        treasury_10y = self.get_latest_value(self.SERIES_IDS["treasury_10y"])
        if treasury_10y:
            snapshot["treasury_10y"] = round(treasury_10y, 2)
        
        # 5. 2년물 국채 수익률 (역전 여부 확인)
        treasury_2y = self.get_latest_value(self.SERIES_IDS["treasury_2y"])
        if treasury_2y:
            snapshot["treasury_2y"] = round(treasury_2y, 2)
            if treasury_10y:
                snapshot["yield_curve_inverted"] = treasury_2y > treasury_10y
        
        # 6. VIX (변동성 지수)
        vix = self.get_latest_value(self.SERIES_IDS["vix"])
        if vix:
            snapshot["vix"] = round(vix, 2)
        
        snapshot["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return snapshot
    
    def analyze_macro_conditions(self) -> Dict[str, Any]:
        """
        거시 경제 상황 종합 분석
        
        Returns:
            {
                "score": 65,  # 0~100
                "grade": "양호",
                "details": [...],
                "risks": [...]
            }
        """
        snapshot = self.get_macro_snapshot()
        
        score = 50  # 기본 점수
        details = []
        risks = []
        
        # 1. 금리 분석
        if "fed_funds_rate" in snapshot:
            rate = snapshot["fed_funds_rate"]
            if rate < 2:
                score += 10
                details.append(f"✅ 저금리 환경 ({rate}%) - 주식 시장에 우호적")
            elif rate > 5:
                score -= 10
                details.append(f"⚠️ 고금리 환경 ({rate}%) - 성장주에 부담")
                risks.append("고금리로 인한 기업 자금 조달 비용 증가")
            else:
                details.append(f"💡 중립 금리 ({rate}%)")
        
        # 2. 인플레이션 분석
        if "cpi_yoy" in snapshot:
            cpi = snapshot["cpi_yoy"]
            if cpi < 2.5:
                score += 10
                details.append(f"✅ 안정적 인플레이션 ({cpi}%)")
            elif cpi > 4:
                score -= 15
                details.append(f"⚠️ 높은 인플레이션 ({cpi}%) - 추가 금리 인상 가능성")
                risks.append("인플레이션 압력으로 인한 금리 인상 리스크")
            else:
                details.append(f"💡 인플레이션 {cpi}% (목표치 2% 상회)")
        
        # 3. 실업률 분석
        if "unemployment_rate" in snapshot:
            unemp = snapshot["unemployment_rate"]
            if 3.5 <= unemp <= 4.5:
                score += 10
                details.append(f"✅ 건강한 고용 시장 (실업률 {unemp}%)")
            elif unemp > 5:
                score -= 10
                details.append(f"⚠️ 고용 시장 약화 (실업률 {unemp}%)")
                risks.append("고용 시장 둔화로 인한 소비 감소 우려")
            else:
                details.append(f"💡 실업률 {unemp}%")
        
        # 4. 수익률 곡선 분석
        if snapshot.get("yield_curve_inverted"):
            score -= 20
            details.append("🚨 수익률 곡선 역전 - 경기 침체 신호")
            risks.append("수익률 곡선 역전은 역사적으로 경기 침체 선행 지표")
        elif "treasury_10y" in snapshot and "treasury_2y" in snapshot:
            spread = snapshot["treasury_10y"] - snapshot["treasury_2y"]
            if spread > 0.5:
                score += 5
                details.append(f"✅ 정상 수익률 곡선 (스프레드 {spread:.2f}%)")
        
        # 5. VIX 분석
        if "vix" in snapshot:
            vix = snapshot["vix"]
            if vix < 15:
                score += 5
                details.append(f"✅ 낮은 변동성 (VIX {vix})")
            elif vix > 25:
                score -= 10
                details.append(f"⚠️ 높은 변동성 (VIX {vix}) - 시장 불안")
                risks.append("높은 변동성으로 인한 급격한 가격 변동 가능")
            else:
                details.append(f"💡 VIX {vix} (정상 범위)")
        
        # 점수 범위 제한
        score = max(0, min(100, score))
        
        # 등급 산정
        if score >= 70:
            grade = "우수"
        elif score >= 50:
            grade = "양호"
        elif score >= 30:
            grade = "주의"
        else:
            grade = "경계"
        
        return {
            "score": score,
            "grade": grade,
            "snapshot": snapshot,
            "details": details,
            "risks": risks if risks else ["현재 주요 리스크 없음"],
            "recommendation": self._generate_macro_recommendation(score, grade)
        }
    
    def _generate_macro_recommendation(self, score: int, grade: str) -> str:
        """거시 환경 기반 추천"""
        if score >= 70:
            return "거시 경제 환경이 우호적입니다. 공격적인 투자 전략을 고려할 수 있습니다."
        elif score >= 50:
            return "거시 경제 환경이 양호합니다. 균형 잡힌 포트폴리오를 유지하세요."
        elif score >= 30:
            return "거시 경제에 불확실성이 있습니다. 방어적 포지션을 늘리고 현금 비중을 확대하세요."
        else:
            return "거시 경제 환경이 좋지 않습니다. 리스크 관리를 최우선으로 하고, 안전 자산 비중을 높이세요."
    
    def get_historical_comparison(self, series_id: str, periods: int = 12) -> Dict[str, Any]:
        """과거 데이터와 비교"""
        df = self.get_series(
            series_id,
            start_date=(datetime.now() - timedelta(days=periods*35)).strftime("%Y-%m-%d")
        )
        
        if df is None or df.empty:
            return {}
        
        current = df['value'].iloc[-1]
        avg = df['value'].mean()
        max_val = df['value'].max()
        min_val = df['value'].min()
        
        return {
            "current": round(current, 2),
            "average": round(avg, 2),
            "max": round(max_val, 2),
            "min": round(min_val, 2),
            "percentile": round((current - min_val) / (max_val - min_val) * 100, 1) if max_val != min_val else 50
        }


# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # API 키 설정 필요: https://fred.stlouisfed.org/docs/api/api_key.html
    fred = FREDDataProvider()
    
    # 거시 경제 스냅샷
    snapshot = fred.get_macro_snapshot()
    print("\n=== 거시 경제 스냅샷 ===")
    for key, value in snapshot.items():
        print(f"{key}: {value}")
    
    # 종합 분석
    analysis = fred.analyze_macro_conditions()
    print(f"\n=== 거시 경제 분석 ===")
    print(f"점수: {analysis['score']}/100 ({analysis['grade']})")
    print(f"\n상세 분석:")
    for detail in analysis['details']:
        print(f"  {detail}")
    print(f"\n주요 리스크:")
    for risk in analysis['risks']:
        print(f"  • {risk}")
    print(f"\n추천: {analysis['recommendation']}")
