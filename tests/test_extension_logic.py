
# Chrome Extension Logic Simulator
# sidepanel.js의 로직을 파이썬으로 동일하게 구현하여 테스트

class MockWindow:
    def __init__(self, href):
        self.href = href
        self.location = self

class MockDocument:
    def __init__(self, title, body_text):
        self.title = title
        self.body = type('obj', (object,), {'innerText': body_text})

def check_security_logic(url, title):
    # sidepanel.js의 로직 그대로 가져옴
    url = url.lower()
    title = title.lower()
    
    valid_domains = [
        "finance", "stock", "invest", "trading", "crypto", "upbit", "bithumb", "coin", "koreaex",
        "naver.com", "daum.net", "yahoo", "google.com/finance", "tossinvest", "bloomberg",
        "cnbc", "wsj", "reuters", "hankyung", "mk.co.kr", "sedaily", "alpha"
    ]
    
    valid_keywords = ["증권", "주식", "금융", "투자", "stock", "market", "finance", "korea exchange"]
    
    is_financial = any(d in url for d in valid_domains) or any(w in title for w in valid_keywords)
    
    return is_financial

def extract_ticker_logic(text, is_financial):
    if not is_financial:
        return "BLOCKED (Not Financial Site)"
        
    import re
    # sidepanel.js의 정규식 로직
    # 1. (Code) format
    paren_match = re.search(r'\(([A-Z]{2,5}|[0-9]{6}(\.[A-Z]{2})?)\)', text)
    if paren_match:
        return paren_match.group(1).replace('.KS', '')
        
    # 2. URL quote format (simulated by text check here)
    if '/quote/' in text:
        url_match = re.search(r'/quote/([A-Z]{1,5})', text)
        if url_match: return url_match.group(1)

    # 3. 6-digit code
    kr_match = re.search(r'\b([0-9]{6})\b', text)
    if kr_match:
        return kr_match.group(1)
        
    return "NULL (No Ticker Found)"

def run_test_cases():
    test_cases = [
        {
            "name": "Case 1: 네이버 증권 (삼성전자)",
            "url": "https://finance.naver.com/item/main.naver?code=005930",
            "title": "삼성전자 : 네이버 증권",
            "body": "삼성전자 005930 현재가 70,000원 전일대비..."
        },
        {
            "name": "Case 2: 야후 파이낸스 (테슬라)",
            "url": "https://finance.yahoo.com/quote/TSLA",
            "title": "Tesla, Inc. (TSLA) Stock Price, News, Quote & History",
            "body": "Tesla, Inc. (TSLA) NasdaqGS - NasdaqGS Real Time Price..."
        },
        {
            "name": "Case 3: 유튜브 (일반 영상 - 아이유)",
            "url": "https://www.youtube.com/watch?v=12345",
            "title": "아이유(IU) - Love poem [MV]",
            "body": "아이유의 새로운 앨범..."
        },
        {
            "name": "Case 4: 쿠팡 (쇼핑몰)",
            "url": "https://www.coupang.com/np/products/123",
            "title": "쿠팡! - 맥북 프로 M3",
            "body": "Apple 2024 맥북프로 14..."
        },
        {
            "name": "Case 5: 유튜브 (주식 강의 영상)",
            "url": "https://www.youtube.com/watch?v=stock123",
            "title": "초보자를 위한 주식 투자 기초 강의",
            "body": "오늘은 주식 시장의 원리에 대해..."
        }
    ]
    
    print(f"{'TEST CASE':<40} | {'ALLOWED?':<10} | {'RESULT'}")
    print("-" * 80)
    
    for case in test_cases:
        is_allowed = check_security_logic(case['url'], case['title'])
        # ticker extraction using the body text
        result = extract_ticker_logic(case['body'], is_allowed)
        
        status = "[PASS]" if is_allowed else "[BLOCK]"
        print(f"{case['name']:<40} | {status:<10} | {result}")

if __name__ == "__main__":
    run_test_cases()
