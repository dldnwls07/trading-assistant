"""
XGBoost 기반 주가 예측 엔진.

레버리지 ETF 처리 원칙:
- 레버리지 ETF(SOXL, NVDL 등)는 기초 자산 데이터로 별도 학습하고,
  예측값에 배수 × 복리 감쇠 보정값(0.88)을 곱해 반환합니다.
- 이 로직은 `LeveragedETFDetector`에 완전히 위임되어 있으므로
  새로운 레버리지 ETF가 출시되어도 이 파일을 수정할 필요가 없습니다.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List, Tuple, Optional
import logging
from src.utils.advanced_indicators import AdvancedIndicators
from src.utils.leveraged_etf_detector import get_detector

logger = logging.getLogger(__name__)


class MLPricePredictor:
    """
    XGBoost 기반 주가 예측 엔진.
    주요 기술적 지표를 피처로 사용하여 미래 가격 변동성을 예측합니다.

    레버리지 ETF 감지는 LeveragedETFDetector에 위임합니다.
    """

    # 일일복리 감쇠 보정 (leverage decay 현상 반영)
    # 이유: 레버리지 ETF는 매일 리밸런싱되므로 장기 보유 시 기초자산 대비
    #       수익이 배수보다 낮아짐. 5거래일 기준 0.85~0.90이 현실에 가깝습니다.
    LEVERAGE_DECAY_FACTOR = 0.88

    def __init__(self, model_path: Optional[str] = None):
        self.model = xgb.XGBRegressor(
            n_estimators=1000,
            learning_rate=0.01,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            n_jobs=-1,
            random_state=42,
            objective='reg:squarederror'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_cols = []

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """피처 엔지니어링: 기술 지표 및 파생 변수 생성"""
        df = df.copy()

        # 1. 고급 지표 계산
        df = AdvancedIndicators.calculate_all(df)

        # 2. 추가 파생 피처 생성
        df['returns_1d'] = df['Close'].pct_change(1)
        df['returns_5d'] = df['Close'].pct_change(5)
        df['volatility_20d'] = df['returns_1d'].rolling(20).std()

        # 가격 위치 정보 (SMA 대비 거리)
        df['dist_from_sma20'] = (df['Close'] - df['sma_20']) / df['sma_20']
        df['dist_from_sma60'] = (df['Close'] - df['sma_60']) / df['sma_60']

        # 3. 모델에 사용할 피처 목록 정의
        cols = [
            'rsi', 'macd', 'macd_signal', 'macd_hist',
            'bb_upper', 'bb_middle', 'bb_lower',
            'sma_20', 'sma_60', 'sma_120',
            'returns_1d', 'returns_5d', 'volatility_20d',
            'dist_from_sma20', 'dist_from_sma60'
        ]

        # 실제 존재하는 컬럼만 필터링
        self.feature_cols = [c for c in cols if c in df.columns]

        # 결측치 제거
        df = df.dropna(subset=self.feature_cols)

        return df, self.feature_cols

    def train(self, df: pd.DataFrame, target_days: int = 5) -> Dict[str, Any]:
        """모델 학습: n일 후의 수익률 예측"""
        try:
            if len(df) < 100:
                return {"success": False, "message": "학습을 위한 데이터가 충분하지 않습니다 (최소 100일 필요)."}

            data, features = self.prepare_features(df)

            # Target: n일 후의 수익률
            data['target'] = data['Close'].shift(-target_days).pct_change(target_days)
            data = data.dropna(subset=['target'])

            if len(data) < 50:
                return {"success": False, "message": "유효한 학습 샘플이 부족합니다."}

            X = data[features]
            y = data['target']

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

            # 피처 스케일링
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # 학습
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_test_scaled, y_test)],
                verbose=False
            )

            self.is_trained = True

            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)

            return {
                "success": True,
                "train_score": train_score,
                "test_score": test_score,
                "feature_importance": dict(zip(features, self.model.feature_importances_.tolist()))
            }

        except Exception as e:
            logger.error(f"모델 학습 중 오류 발생: {e}")
            return {"success": False, "message": str(e)}

    def predict_next(self, df: pd.DataFrame, ticker: str = "") -> Dict[str, Any]:
        """
        최신 데이터를 바탕으로 미래 변동률을 예측합니다.

        레버리지 ETF인 경우 (LeveragedETFDetector가 감지):
          1. 기초 자산 데이터를 yfinance로 수집
          2. 기초 자산으로 독립 MLPricePredictor 학습 후 예측
          3. 예측값 × 배수 × LEVERAGE_DECAY_FACTOR를 최종 결과로 반환

        일반 종목인 경우:
          해당 종목 데이터로 직접 학습 및 예측을 수행합니다.
        """
        ticker_upper = ticker.upper().strip() if ticker else ""

        # --- 레버리지 ETF 감지 (LeveragedETFDetector에 위임) ---
        if ticker_upper:
            leverage_info = get_detector().detect(ticker_upper)
            if leverage_info is not None:
                return self._predict_leveraged(df, ticker_upper, leverage_info)

        # --- 일반 종목: 직접 학습 후 예측 ---
        return self._predict_direct(df)

    def _predict_leveraged(
        self,
        df: pd.DataFrame,
        ticker: str,
        leverage_info: Tuple[str, float]
    ) -> Dict[str, Any]:
        """
        레버리지 ETF 예측 로직.
        기초 자산 데이터를 수집 후, 독립 모델로 예측하고 배수를 적용합니다.
        실패 시 직접 예측으로 폴백합니다.
        """
        base_ticker, leverage_mult = leverage_info
        logger.info(f"레버리지 ETF 감지: {ticker} → {base_ticker} ({leverage_mult:+.1f}x) 기반 예측 시작")

        try:
            import yfinance as yf

            base_df = yf.download(
                base_ticker, period="2y", interval="1d",
                auto_adjust=True, progress=False
            )
            if base_df is None or base_df.empty:
                raise ValueError(f"{base_ticker} 기초 자산 데이터 수집 실패")

            # MultiIndex 컬럼 처리 (yfinance v0.2+ 호환)
            if isinstance(base_df.columns, pd.MultiIndex):
                base_df.columns = base_df.columns.get_level_values(0)
            base_df = base_df.dropna()
            logger.info(f"{base_ticker} 기초 데이터 수집 완료: {len(base_df)}행")

            # 기초 자산으로 독립 모델 인스턴스 생성 후 예측
            # 이유: 같은 인스턴스를 재사용하면 스케일러/피처 상태가 오염될 수 있음
            base_predictor = MLPricePredictor()
            # base_ticker를 전달하지 않아 무한 재귀 방지 (기초 자산은 레버리지 ETF가 아님)
            base_result = base_predictor._predict_direct(base_df)

            if not base_result.get("success"):
                raise ValueError(f"{base_ticker} 예측 실패: {base_result.get('message')}")

            base_return = base_result["predicted_return"]

            # 레버리지 배수 × 복리 감쇠 보정 적용
            # 이유: 3x ETF는 매일 리밸런싱되므로 5거래일 기준 단순 3배가 아닌
            #       약 LEVERAGE_DECAY_FACTOR(0.88)배 수준이 현실에 가깝습니다.
            adjusted_return = base_return * leverage_mult * self.LEVERAGE_DECAY_FACTOR
            direction = "상승" if adjusted_return > 0 else "하락"
            confidence = min(95, abs(adjusted_return) * 1000)

            logger.info(
                f"{ticker} 레버리지 예측 완료: "
                f"{base_ticker} {base_return*100:+.2f}% "
                f"× {leverage_mult:+.1f}x × {self.LEVERAGE_DECAY_FACTOR} "
                f"= {adjusted_return*100:+.2f}%"
            )

            return {
                "success": True,
                "predicted_return": float(adjusted_return),
                "direction": direction,
                "confidence": round(confidence, 1),
                "message": (
                    f"향후 5거래일간 약 {adjusted_return*100:+.2f}% {direction} 예상 "
                    f"(기초지수 {base_ticker} {base_return*100:+.2f}% × {leverage_mult:+.0f}x 레버리지 적용)"
                ),
                "base_ticker": base_ticker,
                "base_return": float(base_return),
                "leverage_mult": leverage_mult,
            }

        except Exception as e:
            logger.warning(
                f"레버리지 ETF({ticker}) 기초 자산 기반 예측 실패, "
                f"직접 예측으로 폴백: {e}"
            )
            # 폴백: 해당 종목 데이터로 직접 예측
            return self._predict_direct(df)

    def _predict_direct(self, df: pd.DataFrame) -> Dict[str, Any]:
        """일반 종목 또는 폴백용 직접 예측 로직."""
        if not self.is_trained:
            train_res = self.train(df)
            if not train_res['success']:
                return {"success": False, "message": "모델 학습 실패로 예측이 불가능합니다."}

        data, features = self.prepare_features(df)
        latest_x = data[features].tail(1)

        if latest_x.empty:
            return {"success": False, "message": "예측을 위한 최신 지표가 부족합니다."}

        latest_scaled = self.scaler.transform(latest_x)
        prediction = self.model.predict(latest_scaled)[0]

        direction = "상승" if prediction > 0 else "하락"
        confidence = min(95, abs(prediction) * 1000)  # 변동률 기반 임의 확신도 계산

        return {
            "success": True,
            "predicted_return": float(prediction),
            "direction": direction,
            "confidence": round(confidence, 1),
            "message": f"향후 5거래일간 약 {prediction*100:+.2f}% {direction} 예상"
        }
