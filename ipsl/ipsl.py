"""InterPlanetary Soft Links (IPSL)

Usage:
  ipsl links show [--ipfs=<ipfs> | --https=<https> | --ftp=<ftp> | --address-only]
  ipsl links add --ipfs=<ipfs> [--https=<https>] [--ftp=<ftp>]
  ipsl links merge <ipfs>
  ipsl domains show
  ipsl domains add <pattern>
  ipsl config show
  ipsl (-h | --help)
  ipsl --version

Options:
  --ipfs=<ipfs>   IPFS address
  --https=<https> HTTPS address
  --ftp=<ftp>     FTP address
  <pattern>       Unix shell-style wildcard
  -h --help       Show this screen.
  --version       Show version.

Subcommands:
  links           Add and get link entries; merge other link maps
  domains         Manage domains for merging link maps
  config
"""

import logging
from docopt import docopt

from . import cmd
from . import common


def _setup_logging(level=logging.INFO):
    _log = logging.getLogger('ipsl')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    _log.addHandler(handler)
    _log.setLevel(level)
    return _log


log = _setup_logging(level=logging.DEBUG)
commands = {
    'links': cmd.links,
    'domains': cmd.domains,
    'config': cmd.config,
}


def run():
    args = docopt(__doc__, version='InterPlanetary Soft Links (IPSL) v0.1')
    command = common.utils.select_command(args, commands)
    command.run(args)


if __name__ == '__main__':
    run()
