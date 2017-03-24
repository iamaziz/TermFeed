import click
from click.testing import CliRunner


from termfeed.feed import *

def test_feed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, input='y')
        #print(result.output)
        #assert result.output == 'Hello World!\n'
    # assert result.exit_code == 0
