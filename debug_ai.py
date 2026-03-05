import os
import json
import logging
from dotenv import load_dotenv

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.config import settings
from src.agents.analysis.ai_analyzer import AIAnalyzer

def test_ai_analyzer_direct():
    load_dotenv()
    analyzer = AIAnalyzer()
    
    # Mock analysis data
    mock_data = {
        "ticker": "ORCL",
        "medium_term_indicators": {
            "rsi": 45,
            "Close": 150,
            "sma_50": 140,
            "sma_200": 130,
            "macd": 1.5,
            "macd_signal": 1.0,
            "macd_hist": 0.5
        }
    }
    
    print("\n--- Testing Qwen Implementation ---")
    result = analyzer._generate_with_qwen(mock_data, lang="ko")
    if result:
        print("✅ Qwen Success!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Qwen Failed. Checking Llama fallback...")
        result_llama = analyzer._generate_with_groq_simple(mock_data, lang="ko")
        if result_llama:
            print("✅ Llama Success!")
            print(json.dumps(result_llama, indent=2, ensure_ascii=False))
        else:
            print("❌ All Groq models failed.")

if __name__ == "__main__":
    test_ai_analyzer_direct()
