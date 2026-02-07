"""
AI Analysis Module

Prepares market data and prompts for LLM-based technical analysis.
Focuses on preventing hallucinations by pre-calculating indicators in Python.
"""

import pandas as pd


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators using Python (to avoid LLM math errors).
    """
    df = df.copy()
    # Moving Averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    # Bollinger Bands (20, 2)
    df["BB_Upper"] = df["MA20"] + (df["Close"].rolling(window=20).std() * 2)
    df["BB_Lower"] = df["MA20"] - (df["Close"].rolling(window=20).std() * 2)

    # MACD (12, 26, 9)
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # RSI (Relative Strength Index) - Simple implementation
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def generate_analysis_prompt(ticker: str, df: pd.DataFrame) -> str:
    """
    Generates a structured prompt for the AI model.

    Strategy:
    1. Provide context (Persona).
    2. Provide PRE-CALCULATED data (Grounding).
    3. Ask for specific output format (Chain of Thought).
    """
    # 1. Pre-calculate indicators
    df_ind = calculate_indicators(df)
    latest = df_ind.iloc[-1]
    prev = df_ind.iloc[-2]
    
    # Determine MACD Status
    macd_status = "Bullish" if latest["MACD"] > latest["MACD_Signal"] else "Bearish"
    bb_position = (latest["Close"] - latest["BB_Lower"]) / (latest["BB_Upper"] - latest["BB_Lower"])

    # 2. Format Data Summary (Numerical Context)
    data_summary = f"""
    [Market Data for {ticker.upper()}]
    - Current Price: {latest['Close']:.2f}
    - Previous Price: {prev['Close']:.2f}
    - Daily Change: {((latest['Close'] - prev['Close']) / prev['Close'] * 100):.2f}%
    - Volume: {latest['Volume']} (vs Avg: {df['Volume'].mean():.0f})

    [Technical Indicators (Pre-calculated)]
    - RSI (14): {latest['RSI']:.2f} (Over 70=Overbought, Under 30=Oversold)
    - MA20: {latest['MA20']:.2f}
    - MA50: {latest['MA50']:.2f}
    - MA200: {latest['MA200']:.2f}
    - Bollinger Bands: Upper {latest['BB_Upper']:.2f} / Lower {latest['BB_Lower']:.2f} (Position: {bb_position:.2f} where 0=Lower, 1=Upper)
    - MACD: {latest['MACD']:.2f} (Signal: {latest['MACD_Signal']:.2f}) -> {macd_status}

    [Trend Context]
    - Price vs MA200: {"Above" if latest['Close'] > latest['MA200'] else "Below"} (Long-term trend)
    - MA50 vs MA200: {"Golden Cross" if latest['MA50'] > latest['MA200'] else "Death Cross/Bearish"}
    """

    # 3. Construct the Prompt
    prompt = f"""
    You are an expert Chartered Market Technician (CMT) and Hedge Fund Portfolio Manager.
    Your goal is to provide a detailed technical analysis and actionable trading advice for {ticker}.
    Focus on identifying entry/exit points and managing risk.

    {data_summary}

    ### Instructions:
    1. **Trend & Momentum**: Analyze the trend using MAs and MACD. Is the momentum strengthening or weakening?
    2. **Key Levels**: Identify potential Support and Resistance levels based on the provided data (MAs, Bollinger Bands).
    3. **Strategy & Setup**:
       - Suggest a specific **Entry Price** range (if bullish).
       - Suggest a **Target Price (Take Profit)** based on resistance or trend extension.
       - Suggest a **Stop Loss** level to manage risk.
    4. **Verdict**: [STRONG BUY / BUY / HOLD / SELL / STRONG SELL]
    5. **Scenario Analysis**:
       - Bull Case: If price breaks above [Level], expect move to...
       - Bear Case: If price breaks below [Level], expect drop to...

    ### Constraints:
    - Do NOT calculate new indicators yourself. Use the provided values.
    - Be concise and professional.
    - If data is insufficient (e.g., NaN values), state that clearly.
    """

    return prompt


# Example usage for testing
if __name__ == "__main__":
    # Mock data would go here
    pass
