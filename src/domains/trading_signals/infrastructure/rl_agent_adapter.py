import os
import torch
import numpy as np
import pandas as pd
import pickle
from typing import Dict, Any, Tuple
from huggingface_hub import hf_hub_download
from stable_baselines3 import PPO

class RLAgentAdapter:
    """
    Adilbai/stock-trading-rl-agent 모델을 활용한 기술적 매매 신호 생성 어댑터
    """
    def __init__(self, repo_id: str = "Adilbai/stock-trading-rl-agent", filename: str = "final_model.zip"):
        self.repo_id = repo_id
        self.filename = filename
        self.model = None
        self.scaler = None

    def load_bundle(self):
        """Hugging Face에서 모델과 스케일러를 다운로드하고 로드합니다."""
        if self.model is not None and self.scaler is not None:
            return

        print(f"📡 Downloading RL bundle from {self.repo_id}...")
        try:
            # Load Model
            model_path = hf_hub_download(repo_id=self.repo_id, filename=self.filename)
            self.model = PPO.load(model_path, device='cpu') # CPU 우선 사용 (CNN 미사용 모델이므로)
            
            # Load Scaler
            scaler_path = hf_hub_download(repo_id=self.repo_id, filename="scaler.pkl")
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
                
            print("✅ RL Model and Scaler loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load RL bundle: {e}")
            raise e

    def predict(self, market_states: np.ndarray, portfolio_state: np.ndarray) -> Tuple[str, float]:
        """
        데이터를 기반으로 다음 행동을 예측합니다.
        시장 상태(3000) + 포트폴리오 상태(8) = 3008 입력 기대
        """
        if self.model is None or self.scaler is None:
            self.load_bundle()
        
        # 1. 시장 데이터 스케일링 (Adilbai 모델은 학습 시 스케일링을 거침)
        # market_states shape: (60, 50)
        # Note: Scaler expects (n_samples, n_features)
        scaled_market = self.scaler.transform(market_states)
        
        # 2. 평탄화 및 결합
        flat_market = scaled_market.flatten() # 3000
        obs = np.concatenate([flat_market, portfolio_state]).astype(np.float32) # 3008
        obs = obs.reshape(1, -1)
        
        # 3. 예측
        action, _states = self.model.predict(obs, deterministic=True)
        
        # action is Box(2,) -> [ActionType, Quantity]
        # ActionType: 0: HOLD / 1: BUY / 2: SELL (정수화)
        action_type_idx = int(np.clip(action[0][0], 0, 2))
        confidence = float(action[0][1]) # 두 번째 차트를 비중/신뢰도로 활용
        
        action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
        return action_map.get(action_type_idx, "HOLD"), confidence
