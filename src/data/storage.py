"""
데이터 저장소 모듈
- SQLite 데이터베이스 관리
- 싱글톤 패턴으로 중복 인스턴스 방지
- Context Manager로 세션 안전 관리
"""
import os
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, selectinload
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


class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=True)  # Stock ticker or 'Econ' for economic events
    alert_type = Column(String)  # 'price_above', 'price_below', 'event'
    target_value = Column(Float, nullable=True)  # Target price
    event_type = Column(String, nullable=True)  # 'CPI', 'FOMC', etc.
    note = Column(String)
    is_active = Column(Integer, default=1)
    triggered_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.now().date())


class VirtualAccount(Base):
    __tablename__ = 'virtual_accounts'
    id = Column(Integer, primary_key=True)
    balance = Column(Float, default=10000000.0)  # 초기 자본 1,000만원
    currency = Column(String, default='KRW')
    updated_at = Column(Date, default=datetime.now().date())


class VirtualPosition(Base):
    __tablename__ = 'virtual_positions'
    id = Column(Integer, primary_key=True)
    ticker = Column(String, ForeignKey('stocks.ticker'))
    quantity = Column(Integer, default=0)
    avg_price = Column(Float, default=0.0)
    updated_at = Column(Date, default=datetime.now().date())


class VirtualTrade(Base):
    __tablename__ = 'virtual_trades'
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    side = Column(String)  # 'BUY', 'SELL'
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(Date, default=datetime.now().date())


# ===========================================
# 싱글톤 DataStorage
# ===========================================

class DataStorage:
    """
    비동기 싱글톤 데이터 저장소
    - SQLAlchemy Async Engine 및 Session 사용
    - Async Context manager로 세션 관리
    """
    _instance: Optional['DataStorage'] = None
    _initialized: bool = False
    
    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if DataStorage._initialized:
            return
        
        self.db_path = db_path or os.getenv("DB_PATH", "trading_assistant.db")
        # aiosqlite 드라이버 사용을 위해 접두어 변경
        self.async_url = f'sqlite+aiosqlite:///{self.db_path}'
        self.engine = create_async_engine(self.async_url, echo=False)
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        DataStorage._initialized = True
        logger.info(f"Async Database initialized at {self.db_path}")

    async def initialize(self):
        """데이터베이스 테이블 생성 (비동기)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def get_session(self):
        """
        비동기 Context manager로 세션 관리
        """
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async Session error: {e}")
                raise
            finally:
                await session.close()
    
    async def save_stock(self, ticker: str, name: str = None, 
                       sector: str = None, industry: str = None) -> Optional[Stock]:
        """종목 정보 저장/업데이트"""
        async with self.get_session() as session:
            result = await session.execute(select(Stock).filter_by(ticker=ticker))
            stock = result.scalar_one_or_none()
            
            if not stock:
                stock = Stock(ticker=ticker, name=name, sector=sector, industry=industry)
                session.add(stock)
            else:
                if name: stock.name = name
                if sector: stock.sector = sector
                if industry: stock.industry = industry
            return stock
    
    async def save_price_history(self, ticker: str, df) -> int:
        """ OHLCV 데이터 저장 """
        await self.save_stock(ticker)
        
        async with self.get_session() as session:
            # 기존 날짜 조회
            result = await session.execute(select(PriceHistory.date).filter(PriceHistory.ticker == ticker))
            existing_dates = {row[0] for row in result.all()}
            
            new_records = []
            for _, row in df.iterrows():
                date_val = row['Date']
                if isinstance(date_val, str):
                    try:
                        date_val = datetime.strptime(date_val.split(' ')[0], '%Y-%m-%d').date()
                    except: continue
                
                if date_val in existing_dates: continue
                
                new_records.append(PriceHistory(
                    ticker=ticker, date=date_val, open=row['Open'],
                    high=row['High'], low=row['Low'], close=row['Close'],
                    volume=row.get('Volume', 0)
                ))
            
            if new_records:
                session.add_all(new_records)
                await session.flush()
                logger.info(f"Saved {len(new_records)} new price records for {ticker}")
            return len(new_records)
    
    async def save_financials(self, ticker: str, financials_data: List[dict]) -> int:
        """재무 데이터 저장"""
        await self.save_stock(ticker)
        saved_count = 0
        async with self.get_session() as session:
            for rec in financials_data:
                result = await session.execute(select(Financials).filter_by(
                    ticker=ticker, period=rec['period'], report_date=rec['report_date']
                ))
                existing = result.scalar_one_or_none()
                if existing:
                    existing.revenue = rec.get('revenue')
                    existing.net_income = rec.get('net_income')
                    existing.eps = rec.get('eps')
                    existing.total_assets = rec.get('total_assets')
                    existing.total_liabilities = rec.get('total_liabilities')
                else:
                    session.add(Financials(
                        ticker=ticker, period=rec['period'], report_date=rec['report_date'],
                        revenue=rec.get('revenue'), net_income=rec.get('net_income'),
                        eps=rec.get('eps'), total_assets=rec.get('total_assets'),
                        total_liabilities=rec.get('total_liabilities')
                    ))
                    saved_count += 1
            return saved_count
    
    async def get_financials(self, ticker: str) -> List[Financials]:
        """재무 데이터 조회"""
        async with self.get_session() as session:
            result = await session.execute(select(Financials).filter_by(ticker=ticker))
            return list(result.scalars().all())
    
    async def get_price_history(self, ticker: str, limit: int = 365) -> List[PriceHistory]:
        """가격 히스토리 조회"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PriceHistory)
                .filter_by(ticker=ticker)
                .order_by(PriceHistory.date.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def save_alert(self, ticker: str, alert_type: str, 
                       target_value: float = None, 
                       event_type: str = None, 
                       note: str = "") -> int:
        """알림 설정 저장"""
        async with self.get_session() as session:
            alert = Alert(
                ticker=ticker,
                alert_type=alert_type,
                target_value=target_value,
                event_type=event_type,
                note=note,
                created_at=datetime.now().date()
            )
            session.add(alert)
            await session.flush()
            return alert.id

    async def get_active_alerts(self, ticker: str = None) -> List[Alert]:
        """활성 알림 조회"""
        async with self.get_session() as session:
            stmt = select(Alert).filter_by(is_active=1)
            if ticker:
                stmt = stmt.filter_by(ticker=ticker)
            result = await session.execute(stmt)
            return list(result.scalars().all())
            
    async def trigger_alert(self, alert_id: int):
        """알림 트리거 (비활성화)"""
        async with self.get_session() as session:
            result = await session.execute(select(Alert).filter_by(id=alert_id))
            alert = result.scalar_one_or_none()
            if alert:
                alert.is_active = 0
                alert.triggered_at = datetime.now().date()

    # --- 가상 매매 관련 메서드 ---
    async def get_virtual_balance(self) -> float:
        """가상 잔고 조회"""
        async with self.get_session() as session:
            result = await session.execute(select(VirtualAccount))
            acc = result.scalar_one_or_none()
            if not acc:
                acc = VirtualAccount(balance=10000000.0)
                session.add(acc)
                await session.flush()
            return acc.balance

    async def update_virtual_balance(self, amount: float):
        """가상 잔고 업데이트"""
        async with self.get_session() as session:
            result = await session.execute(select(VirtualAccount))
            acc = result.scalar_one_or_none()
            if not acc:
                acc = VirtualAccount(balance=10000000.0)
                session.add(acc)
            acc.balance += amount
            acc.updated_at = datetime.now().date()

    async def get_virtual_positions(self) -> List[Dict]:
        """가상 포지션 조회"""
        async with self.get_session() as session:
            result = await session.execute(select(VirtualPosition).filter(VirtualPosition.quantity > 0))
            positions = result.scalars().all()
            return [{"ticker": p.ticker, "quantity": p.quantity, "avg_price": p.avg_price} for p in positions]

    async def update_virtual_position(self, ticker: str, quantity: int, price: float, side: str):
        """가상 포지션 업데이트"""
        async with self.get_session() as session:
            result = await session.execute(select(VirtualPosition).filter_by(ticker=ticker))
            pos = result.scalar_one_or_none()
            if side == 'BUY':
                if not pos:
                    session.add(VirtualPosition(ticker=ticker, quantity=quantity, avg_price=price))
                else:
                    total_cost = (pos.avg_price * pos.quantity) + (price * quantity)
                    pos.quantity += quantity
                    pos.avg_price = total_cost / pos.quantity
            elif side == 'SELL' and pos:
                pos.quantity -= quantity
                if pos.quantity <= 0: await session.delete(pos)
            
            session.add(VirtualTrade(ticker=ticker, side=side, quantity=quantity, price=price))
    
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
