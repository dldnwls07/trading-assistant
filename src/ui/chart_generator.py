"""
차트 시각화 모듈
- 캔들 차트 + 지지/저항선
- 매수/매도 타점 표시
- 이동평균선, 볼린저밴드
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없는 환경 지원
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

logger = logging.getLogger(__name__)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    """
    기술적 분석 차트 생성기
    """
    
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_analysis_chart(
        self, 
        ticker: str, 
        df: pd.DataFrame, 
        analysis_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        분석 데이터를 포함한 기술적 분석 차트 생성
        Returns: 저장된 이미지 경로
        """
        if df is None or len(df) < 20:
            logger.warning("차트 생성을 위한 데이터가 부족합니다")
            return None
        
        try:
            # 최근 60일 데이터만 사용
            df = df.tail(60).copy()
            
            # 인덱스가 날짜가 아니면 변환
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            # 지표 계산
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            # 볼린저 밴드
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            df['BB_Std'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
            df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
            
            # 그래프 생성 (2개 서브플롯: 가격 + 거래량)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                           gridspec_kw={'height_ratios': [3, 1]},
                                           sharex=True)
            
            # === 상단: 가격 차트 ===
            ax1.set_title(f'{ticker} 기술적 분석 차트', fontsize=14, fontweight='bold')
            
            # 캔들스틱 (간소화 버전 - 라인 + 영역)
            ax1.plot(df.index, df['Close'], color='#2196F3', linewidth=2, label='종가')
            ax1.fill_between(df.index, df['Low'], df['High'], alpha=0.1, color='#2196F3')
            
            # 이동평균선
            ax1.plot(df.index, df['SMA_20'], color='#FF9800', linewidth=1.5, 
                    linestyle='--', label='SMA 20')
            if not df['SMA_50'].isna().all():
                ax1.plot(df.index, df['SMA_50'], color='#9C27B0', linewidth=1.5, 
                        linestyle='--', label='SMA 50')
            
            # 볼린저 밴드
            ax1.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], 
                            alpha=0.1, color='gray', label='볼린저밴드')
            ax1.plot(df.index, df['BB_Upper'], color='gray', linewidth=0.8, linestyle=':')
            ax1.plot(df.index, df['BB_Lower'], color='gray', linewidth=0.8, linestyle=':')
            
            # 매수/매도 타점 표시
            entry_points = analysis_data.get('entry_points', {})
            if entry_points:
                current = entry_points.get('current_price', 0)
                buy1 = entry_points.get('buy_target_1', 0)
                buy2 = entry_points.get('buy_target_2', 0)
                sell1 = entry_points.get('sell_target_1', 0)
                stop = entry_points.get('stop_loss', 0)
                
                # 현재가 라인
                if current > 0:
                    ax1.axhline(y=current, color='#2196F3', linewidth=1.5, 
                               linestyle='-', alpha=0.8)
                    ax1.text(df.index[-1], current, f'  현재가: {current:,.0f}', 
                            va='center', fontsize=9, color='#2196F3')
                
                # 매수 타점 (녹색)
                if buy1 > 0:
                    ax1.axhline(y=buy1, color='#4CAF50', linewidth=1.5, 
                               linestyle='--', alpha=0.7)
                    ax1.text(df.index[0], buy1, f'1차 매수: {buy1:,.0f}  ', 
                            va='center', ha='right', fontsize=9, color='#4CAF50')
                
                # 매도 타점 (빨간색)
                if sell1 > 0:
                    ax1.axhline(y=sell1, color='#F44336', linewidth=1.5, 
                               linestyle='--', alpha=0.7)
                    ax1.text(df.index[0], sell1, f'목표가: {sell1:,.0f}  ', 
                            va='center', ha='right', fontsize=9, color='#F44336')
                
                # 손절가 (검정)
                if stop > 0:
                    ax1.axhline(y=stop, color='#000000', linewidth=1, 
                               linestyle=':', alpha=0.5)
                    ax1.text(df.index[0], stop, f'손절: {stop:,.0f}  ', 
                            va='center', ha='right', fontsize=8, color='#666666')
            
            ax1.legend(loc='upper left', fontsize=8)
            ax1.set_ylabel('가격', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # 종합 신호 표시 (이모지 제거)
            signal = analysis_data.get('signal', '관망')
            # 이모지 및 특수문자 제거 (폰트 호환성)
            signal_clean = ''.join(c for c in signal if ord(c) < 0x10000 and not (0x1F300 <= ord(c) <= 0x1F9FF))
            signal_clean = signal_clean.strip()
            if not signal_clean:
                signal_clean = signal.replace('📈', '[매수]').replace('📉', '[매도]').replace('⚠️', '[주의]').replace('🔥', '[강력]')
            
            score = analysis_data.get('final_score', 50)
            signal_color = '#4CAF50' if '매수' in signal else '#F44336' if '매도' in signal else '#FF9800'
            ax1.text(0.98, 0.98, f'{signal_clean}\n점수: {score}/100', 
                    transform=ax1.transAxes, fontsize=12, fontweight='bold',
                    va='top', ha='right', color=signal_color,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # === 하단: 거래량 차트 ===
            if 'Volume' in df.columns:
                colors = ['#4CAF50' if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                         else '#F44336' for i in range(len(df))]
                ax2.bar(df.index, df['Volume'], color=colors, alpha=0.7)
                ax2.set_ylabel('거래량', fontsize=10)
                ax2.grid(True, alpha=0.3)
            
            # X축 날짜 포맷
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            plt.xticks(rotation=45)
            
            # 레이아웃 조정
            plt.tight_layout()
            
            # 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ticker}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            logger.info(f"차트 저장 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"차트 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_mini_chart(self, ticker: str, df: pd.DataFrame) -> Optional[str]:
        """
        오버레이용 미니 차트 생성 (200x150)
        """
        if df is None or len(df) < 10:
            return None
        
        try:
            df = df.tail(30).copy()
            
            fig, ax = plt.subplots(figsize=(3, 2))
            
            # 간단한 라인 차트
            ax.plot(df['Close'].values, color='#2196F3', linewidth=1.5)
            ax.fill_between(range(len(df)), df['Close'].values, alpha=0.1, color='#2196F3')
            
            # 축 숨기기
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            
            # 저장
            filepath = os.path.join(self.output_dir, f"{ticker}_mini.png")
            plt.savefig(filepath, dpi=100, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', pad_inches=0)
            plt.close(fig)
            
            return filepath
            
        except Exception as e:
            logger.error(f"미니 차트 생성 오류: {e}")
            return None
