"""
트레이딩 용어 사전 - 초보자와 전문가 모두를 위한 설명
"""

INDICATOR_DESCRIPTIONS = {
    # === 모멘텀 & 추세 (Momentum & Trend) ===
    "RSI": {
        "name": "상대강도지수 (Relative Strength Index)",
        "beginner": "현재 주가가 '과열'된 상태인지 '공포' 상태인지 알려주는 지표입니다. 70 이상이면 너무 비싸서 떨어질 수 있고, 30 이하면 너무 싸서 오를 수 있습니다.",
        "expert": "가격의 상승 압력과 하락 압력 간의 상대적인 강도를 백분율로 나타냅니다. Wilder의 평활화 방식을 사용하며, 다이버전스 및 Failure Swing을 통해 추세 반전을 조기에 포착합니다."
    },
    "MACD": {
        "name": "이동평균 수렴확산 (MACD)",
        "beginner": "주가의 '분위기'가 바뀌는 걸 포착합니다. 파란 선이 주황 선을 뚫고 올라가면(골든크로스) 매수 신호, 내려가면(데드크로스) 매도 신호입니다.",
        "expert": "단기(12)와 장기(26) 지수이동평균의 수렴과 확산을 통해 추세의 방향과 강도를 진단합니다. 제로라인 돌파는 장기 추세 변화를, 시그널 교차는 단기 진입 시점을 의미합니다."
    },
    "Stochastic": {
        "name": "스토캐스틱 (Stochastic Oscillator)",
        "beginner": "최근 일정 기간 동안의 최고가/최저가 사이에서 현재 가격이 어디쯤인지 알려줍니다. 박스권 장세(횡보장)에서 매매 타이밍을 잡을 때 아주 유용합니다.",
        "expert": "현재 가격의 위치를 %K와 %D선으로 나타내어 침체/과열권을 식별합니다. 추세장보다는 횡보장에서 신뢰도가 높으며, Fast/Slow 설정을 통해 민감도를 조절합니다."
    },
    "CCI": {
        "name": "CCI (Commodity Channel Index)",
        "beginner": "주가가 평균에서 얼마나 멀어졌는지 보여줍니다. 수치가 +100을 넘으면 상승세가 아주 강한 것이고, -100 아래면 하락세가 강한 것입니다.",
        "expert": "주가와 이동평균의 편차를 평균편차로 나누어 산출합니다. 추세의 강도와 방향성을 동시에 보여주며, 사이클의 시작과 끝을 파악하는 데 효과적입니다."
    },
    "ADX": {
        "name": "ADX (Average Directional Index)",
        "beginner": "지금 추세가 얼마나 센지 보여줍니다. 주가가 오르든 내리든 상관없이, 숫자가 클수록(25 이상) 추세가 강력하다는 뜻입니다.",
        "expert": "추세의 강도만을 측정하는 지표입니다. PDI(+DI)와 MDI(-DI)와 함께 사용하여 추세의 방향성을 확인하고, ADX 상승 시 추세 추종 전략을, 하락 시 횡보 전략을 사용합니다."
    },
    "Parabolic SAR": {
        "name": "파라볼릭 SAR (Parabolic Stop And Reverse)",
        "beginner": "주가 흐름을 점으로 찍어 보여줍니다. 점이 주가 아래에 있으면 '상승 추세', 주가 위에 있으면 '하락 추세'입니다. 점의 위치가 바뀌면 추세가 뒤집혔다는 신호입니다.",
        "expert": "시간과 가격을 동시에 고려한 추세 추종 지표입니다. 가속변수(AF)를 사용하여 추세가 가속될수록 지표가 가격에 근접하며, 포지션 청산(Trailing Stop) 기준으로 유용합니다."
    },
    "Williams %R": {
        "name": "윌리엄스 %R (Williams %R)",
        "beginner": "스토캐스틱과 비슷하지만 거꾸로 되어 있습니다. -80 이하면 '너무 싸다(과매도)', -20 이상이면 '너무 비싸다(과매수)'로 해석합니다.",
        "expert": "과매수/과매도 구간을 빠르게 포착하는 모멘텀 지표입니다. 스토캐스틱보다 민감하게 반응하여 단기 반등이나 하락 반전을 조기에 감지할 수 있습니다."
    },

    # === 변동성 & 가격 채널 (Volatility & Channels) ===
    "Bollinger Bands": {
        "name": "볼린저 밴드 (Bollinger Bands)",
        "beginner": "주가가 다니는 '도로'입니다. 보통 도로 안에서 움직이지만, 도로 폭이 좁아지면(차가 막히면) 조만간 뻥 뚫리듯 주가가 크게 움직일 준비를 하는 것입니다.",
        "expert": "이동평균선을 중심으로 표준편차 범위를 밴드로 설정합니다. 밴드폭의 축소(Squeeze)는 변동성 폭발의 전조이며, 밴드 상/하단 태그는 과매수/과매도를 시사합니다."
    },
    "Keltner Channels": {
        "name": "켈트너 채널 (Keltner Channels)",
        "beginner": "볼린저 밴드와 비슷하지만 좀 더 부드럽습니다. 주가가 윗선 뚫고 올라가면 진짜 상승 추세가 시작됐다고 봅니다.",
        "expert": "ATR(평균진폭)을 사용하여 밴드 폭을 설정합니다. 볼린저 밴드보다 속임수 신호가 적으며, 강력한 추세 돌파 매매(Breakout) 전략에 적합합니다."
    },
    "ATR": {
        "name": "ATR (Average True Range)",
        "beginner": "하루에 주가가 평균적으로 얼마나 위아래로 움직이는지 보여줍니다. 이 값이 크면 변동성이 커서 위험할 수 있습니다.",
        "expert": "진정한 변동폭(Gap 포함)을 평균화한 지표입니다. 방향성보다는 변동성의 크기를 측정하며, 손절매 폭(Stop Loss)을 설정하거나 포지션 크기를 조절하는 데 필수적입니다."
    },

    # === 거래량 & 수급 (Volume & Money Flow) ===
    "OBV": {
        "name": "OBV (On-Balance Volume)",
        "beginner": "거래량은 거짓말을 안 합니다. 주가는 제자리인데 OBV가 계속 오르면 누군가 몰래 주식을 모으고 있는 매집 신호일 수 있습니다.",
        "expert": "거래량을 가격 등락에 따라 가감 누적한 지표입니다. 스마트 머니의 유입/유출을 선행적으로 보여주며, 주가와 지표의 다이버전스는 강력한 반전 신호입니다."
    },
    "MFI": {
        "name": "MFI (Money Flow Index)",
        "beginner": "거래량까지 고려한 RSI입니다. 사람들이 돈을 싸들고 들어오는지(매수세), 돈을 빼고 있는지(매도세)를 거래량으로 확인합니다.",
        "expert": "가격과 거래량을 결합하여 자금의 유입/유출 강도를 측정합니다. RSI보다 거짓 신호가 적으며, 80 이상은 과열, 20 이하는 침체로 해석합니다."
    },
    "VWAP": {
        "name": "VWAP (Volume Weighted Average Price)",
        "beginner": "오늘 주식을 산 사람들의 '평균 단가'입니다. 현재 주가가 이 선보다 위에 있으면 매수세가 강하고, 아래에 있으면 매도세가 강한 것입니다.",
        "expert": "거래량 가중 평균 가격으로, 기관 투자자들의 주요 벤치마크입니다. 당일의 추세 지지선이나 저항선으로 작용하며, 알고리즘 트레이딩의 기준점이 됩니다."
    },

    # === 이동평균 & 지지저항 (Moving Averages & Levels) ===
    "SMA": {
        "name": "단순이동평균 (Simple Moving Average)",
        "beginner": "최근 며칠간의 평균 가격입니다. 주가의 뼈대가 되는 선으로, 이 선들이 정배열(단기>중기>장기)이면 상승 추세입니다.",
        "expert": "특정 기간의 종가 평균을 산술적으로 계산합니다. 시장의 노이즈를 제거하여 전반적인 추세를 보여주지만, 후행성이 있어 급변하는 장세에서는 반응이 늦을 수 있습니다."
    },
    "EMA": {
        "name": "지수이동평균 (Exponential Moving Average)",
        "beginner": "최근 가격을 더 중요하게 생각하는 평균선입니다. 주가가 움직일 때 단순이동평균보다 더 빨리 반응해서 단기 매매에 좋습니다.",
        "expert": "최근 데이터에 가중치를 두어 계산합니다. SMA보다 시차(Lag)가 적어 최신 트렌드를 더 빠르게 반영하며, 단기 트레이딩 및 골든/데드크로스 포착에 유리합니다."
    },
    "Pivot Points": {
        "name": "피벗 포인트 (Pivot Points)",
        "beginner": "전날 가격으로 계산한 오늘의 '눈에 안 보이는 벽'입니다. 주가가 오르다가 부딪힐 천장(저항)과 내려가다가 멈출 바닥(지지)을 미리 알려줍니다.",
        "expert": "전일 고가, 저가, 종가를 사용하여 당일의 잠재적 지지/저항 레벨을 산출합니다. 데이트레이더들이 진입/청산 목표가로 가장 많이 참고하는 기준선입니다."
    },
    "Ichimoku Cloud": {
        "name": "일목균형표 (Ichimoku Cloud)",
        "beginner": "구름대(색칠된 부분)만 보세요. 주가가 구름 위에 있으면 맑음(상승), 구름 아래에 있으면 흐림(하락)입니다.",
        "expert": "전환선, 기준선, 후행스팬, 선행스팬으로 구성된 종합 추세 지표입니다. 시간론과 파동론을 결합하여 지지/저항뿐만 아니라 시세의 변곡점까지 예측합니다."
    },

    # === 리스크 & 효율성 (Risk & Efficiency) ===
    "Sharpe Ratio": {
        "name": "샤프 지수 (Sharpe Ratio)",
        "beginner": "투자 가성비 점수입니다. 점수가 높을수록 위험은 적게 지면서 수익은 많이 냈다는 뜻으로, 아주 훌륭한 투자입니다.",
        "expert": "무위험 수익률 대비 포트폴리오의 초과 수익을 표준편차(변동성)로 나눈 값입니다. 변동성 한 단위당 얻은 초과 수익을 의미하며 포트폴리오 성과 평가의 표준입니다."
    },
    "Beta": {
        "name": "베타 계수 (Beta)",
        "beginner": "시장 민감도입니다. 1보다 크면 시장보다 더 크게 움직이고(고수익/고위험), 1보다 작으면 시장보다 얌전하게 움직입니다(저변동성).",
        "expert": "시장 수익률에 대한 개별 자산의 민감도(체계적 위험)입니다. 포트폴리오의 헷징 비율을 산정하거나 CAPM 모델을 통한 기대 수익률 산출에 사용됩니다."
    },
    "AI Score": {
        "name": "AI 종합 점수 (QuantCore AI Score)",
        "beginner": "AI가 수십 가지 데이터를 분석해 내린 성적표입니다. 70점 이상이면 매수 관점, 40점 이하면 매도 관점으로 볼 수 있습니다.",
        "expert": "기술적 지표, 펀더멘털, 시장 감성, 수급 데이터를 앙상블 모델로 종합 분석한 최종 스코어(0~100)입니다. 다각도의 시장 상황을 하나의 정량적 지표로 요약합니다."
    }
}

def get_explanation(indicator_id: str, view: str = "beginner") -> str:
    """
    지표 설명 반환 (검색 매칭 강화)
    Key가 정확히 일치하지 않아도 부분 일치(Case-insensitive)로 찾도록 개선
    """
    # 1. 정확한 매칭 시도
    if indicator_id in INDICATOR_DESCRIPTIONS:
        return INDICATOR_DESCRIPTIONS[indicator_id].get(view, INDICATOR_DESCRIPTIONS[indicator_id]["beginner"])
    
    # 2. 대소문자 무시 및 부분 매칭
    # 예: 'RSI(14)' -> 'RSI', 'sma_20' -> 'SMA'
    normalized_id = indicator_id.upper().replace("_", " ").replace("-", " ")
    
    match_key = None
    
    # 별칭 매핑
    aliases = {
        "RSI": ["RSI", "RELATIVE STRENGTH"],
        "MACD": ["MACD", "MOVING AVERAGE CONVERGENCE"],
        "BOL": ["BOLLINGER", "BB"],
        "STO": ["STOCH", "STOCHASTIC"],
        "Wil": ["WILLIAMS"],
        "SAR": ["PARABOLIC", "SAR"],
        "Piv": ["PIVOT"],
        "SMA": ["SMA", "SIMPLE MO"],
        "EMA": ["EMA", "EXPONENTIAL"],
        "Ichi": ["ICHIMOKU", "CLOUD"],
        "AI": ["AI SCORE", "FINAL SCORE"],
        "Sharpe": ["SHARPE"],
        "Beta": ["BETA"]
    }

    for key, item in INDICATOR_DESCRIPTIONS.items():
        # Key 자체 포함 여부 (RSI_14 -> RSI)
        if key.upper() in normalized_id:
            match_key = key
            break
            
        # 별칭 확인
        for alias_key, alias_list in aliases.items():
            if alias_key.upper() in key.upper(): # 현재 루프의 key가 해당 별칭 그룹인지 확인
                for alias in alias_list:
                    if alias in normalized_id:
                        match_key = key
                        break
            if match_key: break
        if match_key: break
    
    if match_key:
        return INDICATOR_DESCRIPTIONS[match_key].get(view, INDICATOR_DESCRIPTIONS[match_key]["beginner"])
        
    return f"'{indicator_id}'에 대한 설명을 준비 중입니다."
