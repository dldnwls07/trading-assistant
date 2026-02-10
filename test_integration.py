"""
통합 테스트 스크립트
모든 신규 기능 테스트 및 검증
"""
import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pattern_detector():
    """차트 패턴 감지 테스트"""
    logger.info("=== 1. 차트 패턴 감지 테스트 ===")
    try:
        from src.agents.pattern_detector import AdvancedPatternDetector
        import yfinance as yf
        
        detector = AdvancedPatternDetector()
        ticker = yf.Ticker("AAPL")
        df = ticker.history(period="6mo")
        
        patterns = detector.detect_all_patterns(df)
        
        logger.info(f"✅ 감지된 패턴: {len(patterns)}개")
        for i, p in enumerate(patterns[:5], 1):
            logger.info(f"  {i}. {p['name']} - 신뢰도: {p['reliability']}/5.0, 확신도: {p.get('confidence', 'N/A')}%")
        
        return True
    except Exception as e:
        logger.error(f"❌ 패턴 감지 테스트 실패: {e}")
        return False

def test_multi_timeframe():
    """다중 시간 프레임 분석 테스트"""
    logger.info("\n=== 2. 다중 시간 프레임 분석 테스트 ===")
    try:
        from src.agents.multi_timeframe import MultiTimeframeAnalyzer
        
        analyzer = MultiTimeframeAnalyzer()
        result = analyzer.analyze_all_timeframes("AAPL")
        
        logger.info(f"✅ 분석 완료: {result['ticker']}")
        logger.info(f"  단기 점수: {result['short_term']['score'] if result['short_term'] else 'N/A'}")
        logger.info(f"  중기 점수: {result['medium_term']['score'] if result['medium_term'] else 'N/A'}")
        logger.info(f"  장기 점수: {result['long_term']['score'] if result['long_term'] else 'N/A'}")
        logger.info(f"  컨센서스: {result['consensus']['consensus']}")
        logger.info(f"  감지된 패턴: {len(result['all_patterns'])}개")
        
        # 타점 확인
        if result['medium_term'] and result['medium_term'].get('entry_points'):
            entry = result['medium_term']['entry_points']
            logger.info(f"  중기 매수 존: {len(entry.get('buy_zone', []))}개")
            logger.info(f"  중기 매도 존: {len(entry.get('sell_zone', []))}개")
        
        return True
    except Exception as e:
        logger.error(f"❌ 다중 시간 프레임 테스트 실패: {e}")
        return False

def test_screener():
    """종목 스크리너 테스트"""
    logger.info("\n=== 3. AI 추천 종목 시스템 테스트 ===")
    try:
        from src.agents.screener import StockScreener
        
        screener = StockScreener()
        
        # 샘플 종목으로 테스트
        sample_tickers = ["AAPL", "MSFT", "GOOGL"]
        recommendations = screener.screen_stocks(
            tickers=sample_tickers,
            investor_style="balanced",
            top_n=3
        )
        
        logger.info(f"✅ 추천 종목: {len(recommendations)}개")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec['ticker']} - 점수: {rec['score']}, 신호: {rec['signal']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 스크리너 테스트 실패: {e}")
        return False

def test_profiler():
    """투자자 프로파일링 테스트"""
    logger.info("\n=== 4. 투자 스타일 프로파일링 테스트 ===")
    try:
        from src.agents.profiler import InvestorProfiler
        
        profiler = InvestorProfiler(profile_path="test_profile.json")
        
        # 샘플 설문 응답
        survey = {
            "risk_tolerance": 3,
            "time_horizon": "medium",
            "loss_tolerance": 3,
            "investment_goal": "balanced",
            "trading_frequency": "monthly"
        }
        
        style = profiler.create_profile_from_survey(survey)
        style_info = profiler.get_style_info(style)
        
        logger.info(f"✅ 분류된 스타일: {style_info['name']}")
        logger.info(f"  설명: {style_info['description']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 프로파일링 테스트 실패: {e}")
        return False

def test_portfolio_analyzer():
    """포트폴리오 분석 테스트"""
    logger.info("\n=== 5. 포트폴리오 AI 평가 테스트 ===")
    try:
        from src.agents.portfolio_analyzer import PortfolioAnalyzer
        
        analyzer = PortfolioAnalyzer()
        
        # 샘플 포트폴리오
        holdings = [
            {"ticker": "AAPL", "shares": 10, "avg_price": 150},
            {"ticker": "MSFT", "shares": 5, "avg_price": 300}
        ]
        
        result = analyzer.analyze_portfolio(holdings)
        
        logger.info(f"✅ 포트폴리오 점수: {result['portfolio_score']}/100")
        logger.info(f"  총 가치: ${result['total_value']:.2f}")
        logger.info(f"  분산도: {result['diversification']['grade']}")
        logger.info(f"  리스크 밸런스: {result['risk_balance']['score']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 포트폴리오 분석 테스트 실패: {e}")
        return False

def test_event_calendar():
    """이벤트 캘린더 테스트"""
    logger.info("\n=== 6. 경제 이벤트 캘린더 테스트 ===")
    try:
        from src.agents.event_calendar import EventCalendar
        
        calendar = EventCalendar()
        result = calendar.get_calendar(tickers=["AAPL"])
        
        logger.info(f"✅ 이벤트 수: {result['total_events']}개")
        logger.info(f"  기간: {result['period']['start']} ~ {result['period']['end']}")
        logger.info(f"  이번 주: {len(result['summary']['this_week'])}개")
        logger.info(f"  중요 이벤트: {len(result['summary']['upcoming_critical'])}개")
        
        return True
    except Exception as e:
        logger.error(f"❌ 이벤트 캘린더 테스트 실패: {e}")
        return False

def test_chat_assistant():
    """AI 채팅 어시스턴트 테스트"""
    logger.info("\n=== 7. AI 채팅 어시스턴트 테스트 ===")
    try:
        from src.agents.chat_assistant import ChatAssistant
        
        assistant = ChatAssistant()
        
        # 테스트 대화
        questions = [
            "안녕하세요!",
            "AAPL 지금 사도 될까요?"
        ]
        
        for q in questions:
            response = assistant.chat(q, context={
                "ticker": "AAPL",
                "current_price": 175.50,
                "analysis": {"final_score": 72, "signal": "매수 권고"}
            })
            logger.info(f"  Q: {q}")
            logger.info(f"  A: {response[:100]}...")
        
        logger.info("✅ 채팅 어시스턴트 정상 작동")
        return True
    except Exception as e:
        logger.error(f"❌ 채팅 어시스턴트 테스트 실패: {e}")
        return False

def test_fred_provider():
    """FRED API 테스트"""
    logger.info("\n=== 8. FRED API 연동 테스트 ===")
    try:
        from src.data.fred_provider import FREDDataProvider
        
        fred = FREDDataProvider()
        
        # API 키 없이도 기본 기능 테스트
        snapshot = fred.get_macro_snapshot()
        
        if snapshot:
            logger.info(f"✅ 거시 경제 스냅샷 수집 완료")
            logger.info(f"  항목 수: {len(snapshot)}개")
        else:
            logger.warning("⚠️ FRED_API_KEY가 설정되지 않았습니다. 일부 기능 제한됨.")
        
        # 분석 기능 테스트
        analysis = fred.analyze_macro_conditions()
        logger.info(f"  거시 점수: {analysis['score']}/100 ({analysis['grade']})")
        
        return True
    except Exception as e:
        logger.error(f"❌ FRED API 테스트 실패: {e}")
        return False

def main():
    """전체 테스트 실행"""
    logger.info("=" * 60)
    logger.info("AI 트레이딩 어시스턴트 통합 테스트 시작")
    logger.info("=" * 60)
    
    tests = [
        ("차트 패턴 감지", test_pattern_detector),
        ("다중 시간 프레임", test_multi_timeframe),
        ("종목 스크리너", test_screener),
        ("투자 프로파일링", test_profiler),
        ("포트폴리오 분석", test_portfolio_analyzer),
        ("이벤트 캘린더", test_event_calendar),
        ("AI 채팅", test_chat_assistant),
        ("FRED API", test_fred_provider)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"테스트 실행 중 오류: {e}")
            results.append((name, False))
    
    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("테스트 결과 요약")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\n총 {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 모든 테스트 통과!")
    else:
        logger.warning(f"⚠️ {total - passed}개 테스트 실패")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
