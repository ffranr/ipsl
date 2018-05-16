import io
import json
import logging

import ipfsapi

from .. import common

log = logging.getLogger('ipsl')


CONFIG_PATH = "/ipsl/config.json"
TEST_CONFIG_PATH = "/ipsl/test_config.json"
TEST_MODE = False


def _init(get_error=False, **_):
    log.debug("Initializing config")
    if get_error is False and get() is not None:
        return

    default_map = {protocol: {} for protocol in common.utils.protocols}
    ipfs_api = common.ipfs.connect()
    default_map_cid = ipfs_api.dag_put(default_map)

    config = {
        "domains": {
            "patterns": [],
            "seen": []
        },
        "map": default_map_cid
    }
    put(config)
    return config


def put(config):
    log.debug("Put config")
    ipfs_api = common.ipfs.connect()
    config = json.dumps(config, indent=4, sort_keys=True)
    config = io.BytesIO(bytes(config, 'utf-8'))

    ipfs_api.files_mkdir("/ipsl", parents=True)

    if TEST_MODE:
        path = TEST_CONFIG_PATH
    else:
        path = CONFIG_PATH
    ipfs_api.files_write(path, config, create=True, truncate=True)


def get(quiet=True, **_):
    log.debug("Get config")
    ipfs_api = common.ipfs.connect()

    if TEST_MODE:
        path = TEST_CONFIG_PATH
    else:
        path = CONFIG_PATH

    try:
        data_bytes = ipfs_api.files_read(path)
        data_str = str(data_bytes, 'utf8')
        data = json.loads(data_str)
        if not quiet:
            print(data_str)
        return data
    except ipfsapi.exceptions.StatusError:
        _init(get_error=True)
        return get(quiet=quiet)


commands = {
    'show': get,
}


def run(args):
    command = common.utils.select_command(args, commands)
    args = common.utils.clean_arguments(args)
    args['quiet'] = False
    command(**args)
