import urllib.request
import urllib.error
import concurrent.futures
import time

def test_cors(url, method="OPTIONS"):
    print(f"\n[CORS] Testing {method} {url} ...")
    try:
        req = urllib.request.Request(
            url, 
            method=method,
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'x-api-key'
            }
        )
        t0 = time.time()
        with urllib.request.urlopen(req) as res:
            t1 = time.time()
            print(f"✅ CORS Success! Code: {res.getcode()} Time: {t1-t0:.2f}s")
            print(f"Headers: {dict(res.headers)}")
    except Exception as e:
        print(f"❌ CORS Failed: {e}")

def test_get(url):
    print(f"-> Starting GET {url} ...")
    try:
        req = urllib.request.Request(
            url, 
            headers={'X-API-Key': 'trading-assistant-secret-2024'}
        )
        t0 = time.time()
        with urllib.request.urlopen(req) as res:
            t1 = time.time()
            data = res.read()
            print(f"✅ Sub-request Success! {url} | Code: {res.getcode()} | Time: {t1-t0:.2f}s | Length: {len(data)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error for {url}: {e.code} / {e.read().decode()}")
        return False
    except Exception as e:
        print(f"❌ Error for {url}: {e}")
        return False

if __name__ == "__main__":
    ticker = "ORCL"
    url1 = f"http://127.0.0.1:8000/analyze/{ticker}?lang=ko"
    url2 = f"http://127.0.0.1:8000/history/{ticker}?interval=1d"
    
    test_cors(url1)
    test_cors(url2)
    
    print("\n[Parallel Test] Starting concurrent GET requests (simulating browser Promise.allSettled)")
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(test_get, url1)
        f2 = executor.submit(test_get, url2)
        concurrent.futures.wait([f1, f2], timeout=30)
    t1 = time.time()
    print(f"\nParallel test finished in {t1-t0:.2f}s")
