import pandas as pd
import pytest

from trading_assist.validation import validate_ohlcv


def make_valid_df():
    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    df = pd.DataFrame(
        {
            "Open": [100, 102, 101],
            "High": [105, 103, 102],
            "Low": [99, 100, 100],
            "Close": [104, 101, 101],
            "Volume": [1000, 1500, 1200],
        },
        index=idx,
    )
    return df


def test_validate_ok():
    df = make_valid_df()
    validate_ohlcv(df)


def test_validate_missing_col():
    df = make_valid_df().drop(columns=["Volume"])
    with pytest.raises(ValueError) as exc:
        validate_ohlcv(df)
    assert "Missing required columns" in str(exc.value)


def test_validate_negative_volume():
    df = make_valid_df()
    df.loc[df.index[0], "Volume"] = -1
    with pytest.raises(ValueError) as exc:
        validate_ohlcv(df)
    assert "Negative volume" in str(exc.value)


def test_validate_non_positive_close():
    df = make_valid_df()
    df.loc[df.index[0], "Close"] = 0
    with pytest.raises(ValueError) as exc:
        validate_ohlcv(df)
    assert "Non-positive close" in str(exc.value)
