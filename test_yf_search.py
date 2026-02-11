import yfinance as yf
import json

def test_search(query):
    print(f"Searching for: {query}")
    search = yf.Search(query, max_results=15)
    print(json.dumps(search.quotes, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_search("TIGER 반도체 TOP10")
    print("-" * 50)
    test_search("현대차")
    print("-" * 50)
    test_search("삼성전자")
