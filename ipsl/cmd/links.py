import json

import logging
import collections

from urllib.parse import quote, unquote

from .. import common
from . import maps
from . import domains

log = logging.getLogger('ipsl')


def _parse_protocols(**kw):
    protocol_addrs = collections.OrderedDict()
    for protocol in common.protocols:
        address = kw.get(protocol)
        if address is None:
            continue

        address = common.utils.clean_address(protocol, address)
        address = quote(address, safe='')

        protocol_addrs[protocol] = address
    return protocol_addrs


def _get_ipfs_address(protocol_addresses, _map):
    for protocol, address in protocol_addresses.items():
        if protocol == 'ipfs':
            ipfs_address = address
            return ipfs_address

        protocol_entries = _map.get(protocol)
        if protocol_entries is None:
            continue

        protocol_links = protocol_entries.get(address)
        if protocol_links is None:
            continue

        ipfs_address = protocol_links['ipfs']
        return ipfs_address


def _get_ipfs_links(ipfs_address, _map):
    protocol_entries = _map.get('ipfs')
    if protocol_entries is None:
        return

    _links = protocol_entries.get(ipfs_address)
    if _links is None:
        return
    return _links


def get(ipfs=None, https=None, ftp=None, quiet=True, **_):
    log.debug("Get links")
    protocol_addresses = _parse_protocols(ipfs=ipfs, https=https, ftp=ftp)
    if len(protocol_addresses) < 1:
        return maps.get(quiet=quiet)

    log.debug("Protocol addresses:\n%s", protocol_addresses)

    _map = maps.get()
    ipfs_address = _get_ipfs_address(protocol_addresses, _map)
    _links = _get_ipfs_links(ipfs_address, _map)
    if _links is None:
        return

    _links['ipfs'] = ipfs_address
    _links = {protocol: unquote(address) for protocol, address in _links.items()}

    if not quiet:
        links_str = json.dumps(_links, indent=4, sort_keys=True)
        print(links_str)
    return _links


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


def _strip_domains(protocol_addrs):
    all_domains = set()
    for protocols, address in protocol_addrs.items():
        if protocols == 'ipfs':
            continue
        domain = address.split('/')[0]
        all_domains.add(domain)
    return all_domains


def add(ipfs=None, https=None, ftp=None, **_):
    log.debug("Add links")
    protocol_addrs = _parse_protocols(ipfs=ipfs, https=https, ftp=ftp)
    assert 'ipfs' in protocol_addrs
    if len(protocol_addrs) < 2:
        raise ValueError("At least two protocol addresses required")
    log.debug("Protocol addresses:\n%s", protocol_addrs)

    _map = maps.get()
    _map = _add_protocol_entries(_map, protocol_addrs)
    maps.put(_map)

    for domain in _strip_domains(protocol_addrs):
        domains.add(seen=domain)


commands = {
    'show': get,
    'add': add,
    'merge': maps.add
}


def run(args):
    command = common.utils.select_command(args, commands)
    args = common.utils.clean_arguments(args)
    args['quiet'] = False
    command(**args)
