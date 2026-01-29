import pandas as pd
from click.testing import CliRunner

from trading_assist import cli


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


def test_fetch_saves_csv(monkeypatch, tmp_path):
    runner = CliRunner()
    # point DATA_DIR to temporary directory
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path / "data")
    (tmp_path / "data").mkdir()

    df = make_valid_df()

    # mock yf.download to return our DataFrame
    monkeypatch.setattr(cli.yf, "download", lambda *args, **kwargs: df)

    result = runner.invoke(cli.main, ["fetch", "AAPL"])
    assert result.exit_code == 0
    out = result.output
    assert "Saved to" in out
    assert (tmp_path / "data" / "AAPL.csv").exists()


def test_fetch_empty_no_data(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path / "data")
    (tmp_path / "data").mkdir()

    monkeypatch.setattr(cli.yf, "download", lambda *args, **kwargs: pd.DataFrame())

    result = runner.invoke(cli.main, ["fetch", "FAKE"])
    assert result.exit_code != 0
    assert "No data returned" in result.output


def test_fetch_invalid_validation(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path / "data")
    (tmp_path / "data").mkdir()

    # return DataFrame missing required 'Close' column
    df = make_valid_df().drop(columns=["Close"])
    monkeypatch.setattr(cli.yf, "download", lambda *args, **kwargs: df)

    result = runner.invoke(cli.main, ["fetch", "BAD"])
    assert result.exit_code != 0
    assert "Data validation failed" in result.output


def test_summary_requires_fetch(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path / "data")
    # no data file present

    result = runner.invoke(cli.main, ["summary", "MSFT"])
    assert result.exit_code != 0
    assert "Data for MSFT not found" in result.output


def test_summary_outputs_values(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path / "data")
    (tmp_path / "data").mkdir()

    df = make_valid_df()
    filepath = tmp_path / "data" / "TSLA.csv"
    df.to_csv(filepath)

    result = runner.invoke(cli.main, ["summary", "TSLA"])
    assert result.exit_code == 0
    assert "TSLA - Close" in result.output
    assert "Volume" in result.output
