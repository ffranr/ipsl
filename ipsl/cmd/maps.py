import json
import logging
import fnmatch

from urllib.parse import unquote

from .. import common
from . import config
from . import domains


log = logging.getLogger('ipsl')


def _matched_addresses(protocol_map, patterns):
    for address, entry in protocol_map.items():
        _domain = address.split("/")[0]
        match = any(fnmatch.fnmatch(_domain, pattern) for pattern in patterns)
        if not match:
            continue
        ipfs_addr = entry["ipfs"]
        yield ipfs_addr


def _add_ipfs_entry(_map, protocol_addrs):
    location_protocols_mapping = {
        _protocol: _addr
        for _protocol, _addr in protocol_addrs.items()
        if _protocol != 'ipfs' and _addr is not None
    }
    entry = {protocol_addrs['ipfs']: location_protocols_mapping}
    _map['ipfs'].update(entry)
    return _map


def _add_protocol_entries(_map, protocol_addrs):
    _map = _add_ipfs_entry(_map, protocol_addrs)
    for protocol, address in protocol_addrs.items():
        if protocol == 'ipfs':
            continue
        entry = {address: {'ipfs': protocol_addrs['ipfs']}}
        _map[protocol].update(entry)
    return _map


def _add_links(ipfs_addr, secondary_map, _map):
    ipfs_entries = secondary_map["ipfs"][ipfs_addr]

    # filter for locally supported protocols
    filtered_entries = {}
    for protocol in common.protocols:
        if protocol not in ipfs_entries:
            continue
        filtered_entries[protocol] = ipfs_entries[protocol]

    filtered_entries["ipfs"] = ipfs_addr
    _add_protocol_entries(_map, filtered_entries)


def add(ipfs=None, **_):
    log.debug("Add maps")

    _domains = domains.get()
    patterns = _domains["patterns"]
    if not patterns:
        log.debug("No domain patterns: map not parsed")
        return

    ipfs_api = common.ipfs.connect()
    _config = config.get()
    map_cid = _config["map"]

    _map = ipfs_api.dag_get(map_cid)
    secondary_map = ipfs_api.dag_get(ipfs)

    for protocol in common.protocols:
        if protocol == 'ipfs':
            continue
        protocol_map = secondary_map.get(protocol)
        if protocol_map is None:
            continue

        for _ipfs_addr in _matched_addresses(protocol_map, patterns):
            _add_links(_ipfs_addr, secondary_map, _map)

    put(_map)


def _unquote_map(_map):
    unquoted_map = {}
    for protocol in _map:
        unquoted_map.setdefault(protocol, {})
        for address_1 in _map[protocol]:
            addr_1_unquoted = unquote(address_1)
            unquoted_map[protocol].setdefault(addr_1_unquoted, {})
            for protocol_2, address_2 in _map[protocol][address_1].items():
                addr_2_unquoted = unquote(address_2)
                unquoted_map[protocol][addr_1_unquoted][protocol_2] = addr_2_unquoted
    return unquoted_map


def get(address_only=None, quiet=True, **_):
    log.debug("Get maps")

    _config = config.get()
    map_cid = _config["map"]

    if address_only:
        if not quiet:
            print(map_cid)
        return map_cid

    ipfs_api = common.ipfs.connect()
    _map = ipfs_api.dag_get(map_cid)

    if not quiet:
        unquoted_map = _unquote_map(_map)
        map_str = json.dumps(unquoted_map, indent=4, sort_keys=True)
        print(map_str)
    return _map


def put(_map):
    log.debug("Put maps")

    ipfs_api = common.ipfs.connect()
    new_cid = ipfs_api.dag_put(_map)

    _config = config.get()

    # old_cid = _config["map"]
    # TODO: ipfs_api.pin_rm(old_cid) ?

    _config["map"] = new_cid
    config.put(_config)
