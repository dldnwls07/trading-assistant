import logging
import asyncio
import pandas as pd
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, selectinload

from src.config import settings

logger = logging.getLogger(__name__)
Base = declarative_base()

# ... (Previous Model definitions remain unchanged) ...

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
    period = Column(String)
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
    ticker = Column(String, nullable=True)
    alert_type = Column(String)
    target_value = Column(Float, nullable=True)
    event_type = Column(String, nullable=True)
    note = Column(String)
    is_active = Column(Integer, default=1)
    triggered_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.now().date())

class CustomAgent(Base):
    __tablename__ = 'custom_agents'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    llm_weight = Column(Float, default=0.5)
    rl_weight = Column(Float, default=0.5)
    risk_tolerance = Column(String, default='medium')
    base_llm = Column(String, default='gemini')
    initial_balance = Column(Float, default=10000000.0)
    is_active = Column(Integer, default=1)
    created_at = Column(Date, default=datetime.now().date())

class VirtualAccount(Base):
    __tablename__ = 'virtual_accounts'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('custom_agents.id'), nullable=True)
    balance = Column(Float, default=10000000.0)
    currency = Column(String, default='KRW')
    updated_at = Column(Date, default=datetime.now().date())

class VirtualPosition(Base):
    __tablename__ = 'virtual_positions'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('custom_agents.id'), nullable=True)
    ticker = Column(String, ForeignKey('stocks.ticker'))
    quantity = Column(Integer, default=0)
    avg_price = Column(Float, default=0.0)
    updated_at = Column(Date, default=datetime.now().date())

class VirtualTrade(Base):
    __tablename__ = 'virtual_trades'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('custom_agents.id'), nullable=True)
    ticker = Column(String)
    side = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(Date, default=datetime.now().date())

class EconomicEvent(Base):
    __tablename__ = 'economic_events'
    id = Column(Integer, primary_key=True)
    event_key = Column(String, unique=True) # 중복 저장을 방지하기 위한 키 (date_title)
    date = Column(Date)
    time = Column(String)
    country = Column(String)
    title = Column(String)
    description = Column(String)
    importance = Column(String)
    previous = Column(String)
    forecast = Column(String)
    actual = Column(String)
    category = Column(String)
    impact_score = Column(Float) # Surprise Score 등 계산된 영향력
    ai_pre_analysis = Column(String, nullable=True) # 발표 전 AI 시나리오 분석
    ai_post_analysis = Column(String, nullable=True) # 발표 후 AI 결과 해석
    ai_image_url = Column(String, nullable=True) # 관련 분석 차트 이미지 경로
    updated_at = Column(Date, default=datetime.now().date())

# ===========================================
# 싱글톤 DataStorage 고도화
# ===========================================

class DataStorage:
    """
    비동기 싱글톤 데이터 저장소
    - SQLAlchemy Async Engine 및 Session 사용
    - 중앙 설정(settings) 시스템 통합
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
        
        # settings에서 경로 로드
        self.db_path = db_path or settings.DB_PATH
        self.async_url = f'sqlite+aiosqlite:///{self.db_path}'
        
        self.engine = create_async_engine(
            self.async_url, 
            echo=False,
            pool_pre_ping=True  # 연결 유지 확인
        )
        
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        DataStorage._initialized = True
        logger.info(f"💾 Async Database initialized at {self.db_path}")

    async def initialize(self):
        """데이터베이스 테이블 생성 (비동기)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def get_session(self):
        """비동기 Context manager로 세션 안전 관리"""
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Async Session error: {e}")
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
        """OHLCV 데이터 저장"""
        await self.save_stock(ticker)
        
        async with self.get_session() as session:
            result = await session.execute(select(PriceHistory.date).filter(PriceHistory.ticker == ticker))
            existing_dates = {row[0] for row in result.all()}
            
            new_records = []
            for _, row in df.iterrows():
                if 'Date' not in row:
                    logger.warning(f"Skipping row for {ticker}: 'Date' column missing")
                    continue
                date_val = row['Date']
                
                # Series인 경우 (중복 컬럼 발생 시) 첫 번째 값 선택
                if isinstance(date_val, pd.Series):
                    date_val = date_val.iloc[0]
                
                if isinstance(date_val, str):
                    try:
                        date_val = datetime.strptime(date_val.split(' ')[0], '%Y-%m-%d').date()
                    except: continue
                
                # Timestamp인 경우 date 객체로 변환
                if hasattr(date_val, 'date'):
                    date_val = date_val.date()
                
                if date_val in existing_dates: continue
                
                new_records.append(PriceHistory(
                    ticker=ticker, date=date_val, open=row['Open'],
                    high=row['High'], low=row['Low'], close=row['Close'],
                    volume=row.get('Volume', 0)
                ))
            
            if new_records:
                session.add_all(new_records)
                await session.flush()
                logger.debug(f"Saved {len(new_records)} records for {ticker}")
            return len(new_records)
    
    async def get_financials(self, ticker: str) -> List[Financials]:
        async with self.get_session() as session:
            result = await session.execute(select(Financials).filter_by(ticker=ticker))
            return list(result.scalars().all())
    
    async def get_price_history(self, ticker: str, limit: int = 365) -> List[PriceHistory]:
        async with self.get_session() as session:
            result = await session.execute(
                select(PriceHistory)
                .filter_by(ticker=ticker)
                .order_by(PriceHistory.date.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    # --- 경제 이벤트 관련 ---
    async def save_economic_events(self, events: List[Dict[str, Any]]):
        """경제 이벤트 대량 저장"""
        async with self.get_session() as session:
            for e_data in events:
                # event_key 생성 (date_title)
                event_key = f"{e_data['date']}_{e_data['title']}"
                
                # 중복 체크
                result = await session.execute(select(EconomicEvent).filter_by(event_key=event_key))
                existing = result.scalar_one_or_none()
                
                if not existing:
                    event = EconomicEvent(
                        event_key=event_key,
                        date=datetime.strptime(e_data['date'], "%Y-%m-%d").date() if isinstance(e_data['date'], str) else e_data['date'],
                        time=e_data.get('time', ''),
                        country=e_data.get('country', ''),
                        title=e_data.get('title', ''),
                        description=e_data.get('description', ''),
                        importance=e_data.get('importance', 'low'),
                        previous=e_data.get('previous', '-'),
                        forecast=e_data.get('forecast', '-'),
                        actual=e_data.get('actual', '-'),
                        category=e_data.get('category', 'other'),
                        impact_score=e_data.get('impact_score', 0.0),
                        ai_pre_analysis=e_data.get('ai_pre_analysis'),
                        ai_post_analysis=e_data.get('ai_post_analysis'),
                        ai_image_url=e_data.get('ai_image_url')
                    )
                    session.add(event)
                else:
                    # 기존 데이터 업데이트
                    existing.actual = e_data.get('actual', existing.actual)
                    existing.impact_score = e_data.get('impact_score', existing.impact_score)
                    existing.ai_pre_analysis = e_data.get('ai_pre_analysis', existing.ai_pre_analysis)
                    existing.ai_post_analysis = e_data.get('ai_post_analysis', existing.ai_post_analysis)
                    existing.ai_image_url = e_data.get('ai_image_url', existing.ai_image_url)
                    existing.updated_at = datetime.now().date()
            
            await session.commit()

    async def get_economic_events(self, start_date: str, end_date: str) -> List[EconomicEvent]:
        """지정 기간 경제 이벤트 조회"""
        async with self.get_session() as session:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            e_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            result = await session.execute(
                select(EconomicEvent)
                .filter(EconomicEvent.date >= s_dt, EconomicEvent.date <= e_dt)
                .order_by(EconomicEvent.date.asc(), EconomicEvent.time.asc())
            )
            return list(result.scalars().all())

    # --- 가상 매매 및 알림 로직 (동일하게 유지하되 개선된 세션 방식 적용) ---
    async def save_alert(self, **kwargs) -> int:
        async with self.get_session() as session:
            alert = Alert(**kwargs, created_at=datetime.now().date())
            session.add(alert)
            await session.commit()
            return alert.id

    async def get_active_alerts(self) -> List[Alert]:
        async with self.get_session() as session:
            result = await session.execute(select(Alert).filter_by(is_active=1))
            return list(result.scalars().all())

    async def trigger_alert(self, alert_id: int):
        async with self.get_session() as session:
            await session.execute(
                update(Alert)
                .where(Alert.id == alert_id)
                .values(is_active=0, triggered_at=datetime.now().date())
            )
            await session.commit()

    async def get_virtual_balance(self, agent_id: Optional[int] = None) -> float:
        async with self.get_session() as session:
            result = await session.execute(select(VirtualAccount).filter_by(agent_id=agent_id))
            acc = result.scalar_one_or_none()
            if not acc:
                initial_amt = 10000000.0
                if agent_id:
                    ag_res = await session.execute(select(CustomAgent).filter_by(id=agent_id))
                    ag = ag_res.scalar_one_or_none()
                    if ag: initial_amt = ag.initial_balance
                acc = VirtualAccount(agent_id=agent_id, balance=initial_amt)
                session.add(acc)
                await session.flush()
            return acc.balance

    async def update_virtual_balance(self, amount: float, agent_id: Optional[int] = None):
        async with self.get_session() as session:
            result = await session.execute(select(VirtualAccount).filter_by(agent_id=agent_id))
            acc = result.scalar_one_or_none()
            if not acc:
                acc = VirtualAccount(agent_id=agent_id, balance=10000000.0)
                session.add(acc)
            acc.balance += amount
            acc.updated_at = datetime.now().date()

    async def get_virtual_positions(self, agent_id: Optional[int] = None) -> List[Dict]:
        async with self.get_session() as session:
            result = await session.execute(select(VirtualPosition).filter(VirtualPosition.quantity > 0, VirtualPosition.agent_id == agent_id))
            return [{"ticker": p.ticker, "quantity": p.quantity, "avg_price": p.avg_price} for p in result.scalars().all()]

    async def update_virtual_position(self, ticker: str, quantity: int, price: float, side: str, agent_id: Optional[int] = None):
        async with self.get_session() as session:
            result = await session.execute(select(VirtualPosition).filter_by(ticker=ticker, agent_id=agent_id))
            pos = result.scalar_one_or_none()
            
            if side == 'BUY':
                if not pos:
                    pos = VirtualPosition(agent_id=agent_id, ticker=ticker, quantity=quantity, avg_price=price)
                    session.add(pos)
                else:
                    new_total = pos.quantity + quantity
                    pos.avg_price = ((pos.avg_price * pos.quantity) + (price * quantity)) / new_total
                    pos.quantity = new_total
            elif side == 'SELL':
                if pos and pos.quantity >= quantity:
                    pos.quantity -= quantity
            
            pos.updated_at = datetime.now().date()
            await session.commit()

    # --- 커스텀 에이전트(Custom Agent) 관련 ---
    async def create_custom_agent(self, name: str, llm_weight: float, rl_weight: float, risk_tolerance: str, base_llm: str, initial_balance: float = 10000000.0) -> CustomAgent:
        async with self.get_session() as session:
            agent = CustomAgent(
                name=name, llm_weight=llm_weight, rl_weight=rl_weight,
                risk_tolerance=risk_tolerance, base_llm=base_llm, initial_balance=initial_balance
            )
            session.add(agent)
            await session.commit()
            return agent

    async def get_custom_agents(self, active_only: bool = False) -> List[CustomAgent]:
        async with self.get_session() as session:
            stmt = select(CustomAgent)
            if active_only:
                stmt = stmt.filter_by(is_active=1)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_custom_agent(self, agent_id: int) -> Optional[CustomAgent]:
        async with self.get_session() as session:
            result = await session.execute(select(CustomAgent).filter_by(id=agent_id))
            return result.scalar_one_or_none()

    async def update_custom_agent_status(self, agent_id: int, is_active: int):
        async with self.get_session() as session:
            result = await session.execute(select(CustomAgent).filter_by(id=agent_id))
            agent = result.scalar_one_or_none()
            if agent:
                agent.is_active = is_active
                await session.commit()
                
    async def delete_custom_agent(self, agent_id: int):
        async with self.get_session() as session:
            # Delete associated virtual trades, positions, and account
            await session.execute(delete(VirtualTrade).where(VirtualTrade.agent_id == agent_id))
            await session.execute(delete(VirtualPosition).where(VirtualPosition.agent_id == agent_id))
            await session.execute(delete(VirtualAccount).where(VirtualAccount.agent_id == agent_id))
            # Delete agent
            await session.execute(delete(CustomAgent).where(CustomAgent.id == agent_id))
            await session.commit()

    @classmethod
    def reset_instance(cls):
        cls._instance = None
        cls._initialized = False

# Singleton Factory
def get_storage(db_path: str = None) -> DataStorage:
    return DataStorage(db_path)
