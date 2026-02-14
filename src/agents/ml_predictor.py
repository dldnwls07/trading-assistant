import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List, Tuple, Optional
import logging
from src.utils.advanced_indicators import AdvancedIndicators

logger = logging.getLogger(__name__)

class MLPricePredictor:
    """
    XGBoost 기반 주가 예측 엔진
    주요 기술적 지표를 피처로 사용하여 미래 가격 변동성을 예측
    """
    
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
        
        # 1. 기존 고급 지표 계산 (이미 계산되어 있을 수 있지만 안전을 위해)
        df = AdvancedIndicators.calculate_all(df)
        
        # 2. 추가 피처 생성
        # 변동성 및 모멘텀
        df['returns_1d'] = df['Close'].pct_change(1)
        df['returns_5d'] = df['Close'].pct_change(5)
        df['volatility_20d'] = df['returns_1d'].rolling(20).std()
        
        # 가격 위치 정보
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
            
            # 성능 메트릭 (단순 참고용)
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

    def predict_next(self, df: pd.DataFrame) -> Dict[str, Any]:
        """최신 데이터를 바탕으로 미래 변동률 예측"""
        if not self.is_trained:
            # 학습이 안 되어 있으면 즉석에서 학습 시도 (최근 데이터 기준)
            train_res = self.train(df)
            if not train_res['success']:
                return {"success": False, "message": "모델 학습 실패로 예측이 불가능합니다."}

        # 최신 데이터 피처 추출
        data, features = self.prepare_features(df)
        latest_x = data[features].tail(1)
        
        if latest_x.empty:
            return {"success": False, "message": "예측을 위한 최신 지표가 부족합니다."}
            
        latest_scaled = self.scaler.transform(latest_x)
        prediction = self.model.predict(latest_scaled)[0]
        
        # 방향성 및 강도 해석
        direction = "상승" if prediction > 0 else "하락"
        confidence = min(95, abs(prediction) * 1000) # 변동률 기반 임의 확신도 계산
        
        return {
            "success": True,
            "predicted_return": float(prediction),
            "direction": direction,
            "confidence": round(confidence, 1),
            "message": f"향후 5거래일간 약 {prediction*100:+.2f}% {direction} 예상"
        }
