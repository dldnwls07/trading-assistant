"""
데이터 저장소 모듈
- SQLite 데이터베이스 관리
- 싱글톤 패턴으로 중복 인스턴스 방지
- Context Manager로 세션 안전 관리
"""
import os
import logging
from contextlib import contextmanager
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
Base = declarative_base()


# ===========================================
# 모델 정의
# ===========================================

class Stock(Base):
    __tablename__ = 'stocks'
    
    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    
    prices = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")
    financials = relationship("Financials", back_populates="stock", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, ForeignKey('stocks.ticker'))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    stock = relationship("Stock", back_populates="prices")


class Financials(Base):
    __tablename__ = 'financials'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, ForeignKey('stocks.ticker'))
    period = Column(String)  # '2023-Q4', '2023-FY'
    report_date = Column(Date)
    
    revenue = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    
    stock = relationship("Stock", back_populates="financials")


# ===========================================
# 싱글톤 DataStorage
# ===========================================

class DataStorage:
    """
    싱글톤 패턴 데이터 저장소
    - 하나의 인스턴스만 생성
    - Context manager로 세션 관리
    """
    _instance: Optional['DataStorage'] = None
    _initialized: bool = False
    
    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        # 이미 초기화된 경우 스킵
        if DataStorage._initialized:
            return
        
        # 환경변수 또는 매개변수에서 DB 경로 가져오기
        self.db_path = db_path or os.getenv("DB_PATH", "trading_assistant.db")
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        DataStorage._initialized = True
        logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_session(self):
        """
        Context manager로 세션 관리
        사용법: with storage.get_session() as session:
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def save_stock(self, ticker: str, name: str = None, 
                   sector: str = None, industry: str = None) -> Optional[Stock]:
        """종목 정보 저장/업데이트"""
        with self.get_session() as session:
            stock = session.query(Stock).filter_by(ticker=ticker).first()
            if not stock:
                stock = Stock(ticker=ticker, name=name, sector=sector, industry=industry)
                session.add(stock)
            else:
                if name:
                    stock.name = name
                if sector:
                    stock.sector = sector
                if industry:
                    stock.industry = industry
            return stock
    
    def save_price_history(self, ticker: str, df) -> int:
        """
        OHLCV 데이터 저장
        Returns: 저장된 레코드 수
        """
        # 먼저 종목 확인
        self.save_stock(ticker)
        
        with self.get_session() as session:
            # 기존 날짜 조회 (중복 방지)
            existing_dates = {
                row[0] for row in session.query(PriceHistory.date)
                .filter(PriceHistory.ticker == ticker)
                .all()
            }
            
            new_records = []
            for _, row in df.iterrows():
                date_val = row['Date']
                if date_val in existing_dates:
                    continue
                
                record = PriceHistory(
                    ticker=ticker,
                    date=date_val,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row.get('Volume', 0)
                )
                new_records.append(record)
            
            if new_records:
                session.bulk_save_objects(new_records)
                logger.info(f"Saved {len(new_records)} new price records for {ticker}")
            else:
                logger.info(f"No new records to save for {ticker}")
            
            return len(new_records)
    
    def save_financials(self, ticker: str, financials_data: List[dict]) -> int:
        """
        재무 데이터 저장
        Returns: 저장된 레코드 수
        """
        self.save_stock(ticker)
        saved_count = 0
        
        with self.get_session() as session:
            for rec in financials_data:
                # 기존 레코드 확인
                existing = session.query(Financials).filter_by(
                    ticker=ticker,
                    period=rec['period'],
                    report_date=rec['report_date']
                ).first()
                
                if existing:
                    # 업데이트
                    existing.revenue = rec.get('revenue')
                    existing.net_income = rec.get('net_income')
                    existing.eps = rec.get('eps')
                    existing.total_assets = rec.get('total_assets')
                    existing.total_liabilities = rec.get('total_liabilities')
                else:
                    # 신규 추가
                    new_rec = Financials(
                        ticker=ticker,
                        period=rec['period'],
                        report_date=rec['report_date'],
                        revenue=rec.get('revenue'),
                        net_income=rec.get('net_income'),
                        eps=rec.get('eps'),
                        total_assets=rec.get('total_assets'),
                        total_liabilities=rec.get('total_liabilities')
                    )
                    session.add(new_rec)
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} financial records for {ticker}")
            return saved_count
    
    def get_financials(self, ticker: str) -> List[Financials]:
        """재무 데이터 조회"""
        with self.get_session() as session:
            # 세션 닫히기 전에 데이터 복사 (expunge 사용)
            records = session.query(Financials).filter_by(ticker=ticker).all()
            for r in records:
                session.expunge(r)
            return records
    
    def get_price_history(self, ticker: str, limit: int = 365) -> List[PriceHistory]:
        """가격 히스토리 조회"""
        with self.get_session() as session:
            records = (
                session.query(PriceHistory)
                .filter_by(ticker=ticker)
                .order_by(PriceHistory.date.desc())
                .limit(limit)
                .all()
            )
            for r in records:
                session.expunge(r)
            return records
    
    @classmethod
    def reset_instance(cls):
        """테스트용: 싱글톤 인스턴스 리셋"""
        cls._instance = None
        cls._initialized = False


# 편의를 위한 전역 함수
def get_storage(db_path: str = None) -> DataStorage:
    """DataStorage 싱글톤 인스턴스 반환"""
    return DataStorage(db_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    storage = get_storage()
    print(f"Database path: {storage.db_path}")
