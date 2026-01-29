from click.testing import CliRunner
from trading_assist import cli

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'Fetch OHLCV data' in runner.invoke(cli.main, ['fetch', '--help']).output
