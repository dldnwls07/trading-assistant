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

    [Trend Context]
    - Price vs MA200: {"Above" if latest['Close'] > latest['MA200'] else "Below"} (Long-term trend)
    - MA50 vs MA200: {"Golden Cross" if latest['MA50'] > latest['MA200'] else "Death Cross/Bearish"}
    """

    # 3. Construct the Prompt
    prompt = f"""
    You are an expert Chartered Market Technician (CMT) with 20 years of experience.
    Analyze the following stock data for {ticker} and provide a trading strategy.

    {data_summary}

    ### Instructions:
    1. **Trend Analysis**: Identify the short-term and long-term trend based on MAs.
    2. **Momentum**: Analyze RSI. Is it overbought, oversold, or neutral?
    3. **Volume Analysis**: Is the volume significant compared to the average?
    4. **Verdict**: Provide a clear summary: [BULLISH / BEARISH / NEUTRAL].
    5. **Risk Warning**: Mention one key risk factor based on the data.

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
