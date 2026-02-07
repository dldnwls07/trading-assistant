from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    
    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    
    prices = relationship("PriceHistory", back_populates="stock")
    financials = relationship("Financials", back_populates="stock")

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
    period = Column(String) # '2023-Q4', '2023-FY'
    report_date = Column(Date)
    
    revenue = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    
    stock = relationship("Stock", back_populates="financials")

class DataStorage:
    def __init__(self, db_path: str = "trading_assistant.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized at {db_path}")

    def get_session(self):
        return self.Session()
    
    def save_stock(self, ticker, name=None, sector=None, industry=None):
        session = self.Session()
        try:
            stock = session.query(Stock).filter_by(ticker=ticker).first()
            if not stock:
                stock = Stock(ticker=ticker, name=name, sector=sector, industry=industry)
                session.add(stock)
            else:
                if name: stock.name = name
                if sector: stock.sector = sector
                if industry: stock.industry = industry
            session.commit()
            return stock
        except Exception as e:
            logger.error(f"Error saving stock {ticker}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def save_price_history(self, ticker: str, df):
        """
        Saves OHLCV data from a DataFrame to the database.
        Expects DataFrame to have columns: Date, Open, High, Low, Close, Volume
        """
        session = self.Session()
        try:
            # Ensure stock exists first
            self.save_stock(ticker)
            
            # Get existing dates to avoid duplicates (simple optimization)
            existing_dates = {
                row[0] for row in session.query(PriceHistory.date)
                .filter(PriceHistory.ticker == ticker)
                .all()
            }
            
            new_records = []
            for _, row in df.iterrows():
                date_val = row['Date'] # Already date object from collector
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
                session.commit()
                logger.info(f"Saved {len(new_records)} new price records for {ticker}")
            else:
                logger.info(f"No new records to save for {ticker}")
                
        except Exception as e:
            logger.error(f"Error saving price history for {ticker}: {e}")
            session.rollback()
        finally:
            session.close()

    def save_financials(self, ticker: str, financials_data: list[dict]):
        """
        Saves list of financial records.
        Each dict should contain keys matching Financials model:
        period, report_date, revenue, net_income, eps, total_assets, total_liabilities
        """
        session = self.Session()
        try:
            self.save_stock(ticker)
            
            for rec in financials_data:
                # Check if record exists for this period
                existing = session.query(Financials).filter_by(
                    ticker=ticker, 
                    period=rec['period'],
                    report_date=rec['report_date']
                ).first()
                
                if existing:
                    # Update fields
                    existing.revenue = rec.get('revenue')
                    existing.net_income = rec.get('net_income')
                    existing.eps = rec.get('eps')
                    existing.total_assets = rec.get('total_assets')
                    existing.total_liabilities = rec.get('total_liabilities')
                else:
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
            
            session.commit()
            logger.info(f"Saved {len(financials_data)} financial records for {ticker}")
            
        except Exception as e:
            logger.error(f"Error saving financials for {ticker}: {e}")
            session.rollback()
        finally:
            session.close()

    def get_financials(self, ticker: str):
        """
        Retrieves financial records for a ticker.
        """
        session = self.Session()
        try:
            return session.query(Financials).filter_by(ticker=ticker).all()
        finally:
            session.close()

if __name__ == "__main__":
    storage = DataStorage()
