from fastapi import APIRouter, HTTPException, Query
from . import analysis, config, data_source

router = APIRouter()

@router.get("/health", summary="Check API health")
async def health_check():
    """
    Endpoint to verify that the API is running.
    """
    return {"status": "ok"}


@router.get("/stock/{ticker}/history", summary="Get OHLCV History")
async def get_stock_history(
    ticker: str,
    period: str = Query("1y", description="Data period (e.g., 1d, 5d, 1mo, 1y, 5y, max)"),
    interval: str = Query("1d", description="Data interval (e.g., 1m, 5m, 1h, 1d, 1wk)"),
):
    """
    Fetches historical OHLCV (Open, High, Low, Close, Volume) data for a given stock ticker.
    """
    try:
        df = data_source.fetch(ticker=ticker, period=period, interval=interval)
        # Convert DataFrame to JSON format suitable for charting libraries
        df.index = df.index.strftime('%Y-%m-%d') # Format date index
        return df.to_dict(orient="index")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/stock/{ticker}/analysis/golden-cross", summary="Golden Cross Analysis")
async def get_golden_cross_analysis(
    ticker: str,
    period: str = Query("1y", description="Data period to fetch for analysis"),
    short_window: int = Query(config.DEFAULT_MA_SHORT_WINDOW, description="Short moving average window"),
    long_window: int = Query(config.DEFAULT_MA_LONG_WINDOW, description="Long moving average window"),
):
    """
    Performs a Golden Cross (MA50 vs MA200) analysis on a stock's historical data.
    """
    try:
        df = data_source.fetch(ticker=ticker, period=period, interval="1d")
        result = analysis.calculate_golden_cross(
            df, short_window=short_window, long_window=long_window
        )
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
