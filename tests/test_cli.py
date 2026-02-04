from unittest.mock import patch

import pandas as pd
from click.testing import CliRunner

from trading_assist import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--help"])
    assert result.exit_code == 0
    result2 = runner.invoke(cli.main, ["fetch", "--help"])
    assert "Fetch OHLCV data" in result2.output


def test_financials_success():
    """Test `financials` command success."""
    runner = CliRunner()
    # Create a sample DataFrame to be returned by the mock
    sample_data = {
        "2023-06-30": [200, 100, 50],
        "2022-06-30": [180, 90, 40],
    }
    sample_df = pd.DataFrame(
        sample_data, index=["Total Revenue", "Net Income", "EBITDA"]
    )

    with patch("trading_assist.data_source.get_financials") as mock_get_financials:
        mock_get_financials.return_value = sample_df
        result = runner.invoke(cli.main, ["financials", "MSFT"])

        assert result.exit_code == 0
        assert "Fetching financials for MSFT..." in result.output
        assert "Total Revenue" in result.output
        assert "Net Income" in result.output
        mock_get_financials.assert_called_once_with("MSFT")


def test_financials_failure():
    """Test `financials` command failure."""
    runner = CliRunner()

    with patch("trading_assist.data_source.get_financials") as mock_get_financials:
        mock_get_financials.side_effect = RuntimeError("No data")
        result = runner.invoke(cli.main, ["financials", "FAKETICKER"])

        assert result.exit_code == 1
        assert "Fetching financials for FAKETICKER..." in result.output
        assert "Error: No data" in result.output
        mock_get_financials.assert_called_once_with("FAKETICKER")
