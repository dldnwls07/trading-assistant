import requests
import json
import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class KISClient:
    """
    한국투자증권 Open API Wrapper
    인증, 잔고 조회, 주문 실행 등 핵심 기능 제공
    """
    
    def __init__(self, is_paper: bool = True):
        self.is_paper = is_paper
        self.base_url = "https://openapivts.koreainvestment.com:29443" if is_paper else "https://openapi.koreainvestment.com:29443"
        
        self.app_key = os.getenv("KIS_APP_KEY")
        self.app_secret = os.getenv("KIS_APP_SECRET")
        self.account_no = os.getenv("KIS_ACCOUNT_NO")  # 8자리-2자리 형식 (12345678-01)
        
        self.token = None
        self.token_expired_at = 0
        
        # 계좌 번호 분리
        if self.account_no and '-' in self.account_no:
            self.acc_front, self.acc_back = self.account_no.split('-')
        else:
            self.acc_front = self.account_no
            self.acc_back = "01"

    def _get_access_token(self) -> str:
        """액세스 토큰 발급 및 자동 갱신"""
        # 현재 시간이 토큰 만료 시간 이전이면 기존 토큰 반환 (보통 24시간 유효)
        if self.token and time.time() < self.token_expired_at - 3600:
            return self.token
            
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"Content-Type": "application/json"}
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret
        }
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload))
            res.raise_for_status()
            data = res.json()
            
            self.token = data.get("access_token")
            # expires_in은 보통 86400초(24시간)
            expires_in = int(data.get("expires_in", 86400))
            self.token_expired_at = time.time() + expires_in
            
            logger.info("KIS API 신규 토큰 발급 성공")
            return self.token
        except Exception as e:
            logger.error(f"KIS 토큰 발급 실패: {e}")
            return None

    def _get_headers(self, tr_id: str) -> Dict[str, str]:
        """API 요청 공통 헤더 생성"""
        token = self._get_access_token()
        return {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
        }

    def get_stock_balance(self, is_domestic: bool = True) -> Dict[str, Any]:
        """주식 잔고 조회 (국내/해외)"""
        if is_domestic:
            # TTTC8434R: 주식 현금 잔고 조회
            tr_id = "VTTC8434R" if self.is_paper else "TTTC8434R"
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            params = {
                "CANO": self.acc_front,
                "ACNT_PRDT_CD": self.acc_back,
                "AFHR_FLG": "N",
                "OFR_SNUM": "",
                "IVRE_CHNL_CD": "",
                "PRCS_DVSN": "01",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FSRB_REI_DT": ""
            }
        else:
            # VTTS3012R: 해외주식 잔고 조회 (모의), TTTS3012R (실전)
            tr_id = "VTRP6010R" if self.is_paper else "TRRP6010R" # 통합거치대 잔고
            url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
            # 해외주식용 파라미터는 API 가이드에 따라 조정 필요
            params = {
                "CANO": self.acc_front,
                "ACNT_PRDT_CD": self.acc_back,
                "OVRS_EXCH_CD": "NASD", # 기본 나스닥
                "TR_CRC_CD": "USD",
                "CTX_AREA_FK200": "",
                "CTX_AREA_NK200": ""
            }

        try:
            res = requests.get(url, headers=self._get_headers(tr_id), params=params)
            return res.json()
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
            return {"error": str(e)}

    def get_price(self, ticker: str, is_domestic: bool = True) -> Optional[float]:
        """실시간 현재가 조회"""
        if is_domestic:
            tr_id = "FHKST01010100"
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker}
        else:
            tr_id = "HHDFS00000300"
            url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
            # 시장 코드 판별 로직(NASD, NYSE 등)이 필요하나 우선 간소화
            params = {"AUTH": "", "EXCD": "NAS", "SYMB": ticker}

        try:
            res = requests.get(url, headers=self._get_headers(tr_id), params=params)
            data = res.json()
            if data.get("rt_cd") == "0":
                return float(data["output"]["stck_prpr"]) if is_domestic else float(data["output"]["last"])
            return None
        except Exception as e:
            logger.error(f"{ticker} 시세 조회 실패: {e}")
            return None

    def place_order(self, ticker: str, quantity: int, price: int = 0, is_buy: bool = True, is_domestic: bool = True) -> Dict[str, Any]:
        """주문 접수 (시장가 기본)"""
        # 국내 주식 주문 예시 (TTTC0802U: 매수, TTTC0801U: 매도)
        if is_domestic:
            tr_id = ("VTTC0802U" if is_buy else "VTTC0801U") if self.is_paper else ("TTTC0802U" if is_buy else "TTTC0801U")
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
            
            payload = {
                "CANO": self.acc_front,
                "ACNT_PRDT_CD": self.acc_back,
                "PDNO": ticker,
                "ORD_DVSN": "01", # 01: 시장가
                "ORD_QTY": str(quantity),
                "ORD_UNPR": "0" if price == 0 else str(price)
            }
        else:
            # 해외 주식 주문 (해당 API 명세 확인 필요)
            return {"error": "Overseas order not implemented yet"}

        try:
            res = requests.post(url, headers=self._get_headers(tr_id), data=json.dumps(payload))
            return res.json()
        except Exception as e:
            logger.error(f"주문 실패: {e}")
            return {"error": str(e)}
