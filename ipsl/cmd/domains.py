import json
import logging

from .. import common
from . import config

log = logging.getLogger('ipsl')


def add(pattern=None, seen=None, **_):
    log.debug("Add domains: %s", pattern)
    _config = config.get()

    if seen is not None and seen not in _config["domains"]["seen"]:
        _config["domains"]["seen"].append(seen)

    if pattern is not None and pattern not in _config["domains"]["patterns"]:
        _config["domains"]["patterns"].append(pattern)

    config.put(_config)


def get(quiet=True, **_):
    log.debug("Get domains")
    _config = config.get()
    result = _config["domains"]
    if not quiet:
        domains_str = json.dumps(result, indent=4, sort_keys=True)
        print(domains_str)
    return result


commands = {
    'show': get,
    'add': add,
}


def run(args):
    # Note: seen contains a summary of domains seen
    # patterns describes which domains to lookout for
    command = common.utils.select_command(args, commands)
    args = common.utils.clean_arguments(args)
    args['quiet'] = False
    command(**args)
