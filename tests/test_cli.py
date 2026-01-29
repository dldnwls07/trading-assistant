from click.testing import CliRunner

from trading_assist import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--help"])
    assert result.exit_code == 0
    result2 = runner.invoke(cli.main, ["fetch", "--help"])
    assert "Fetch OHLCV data" in result2.output
