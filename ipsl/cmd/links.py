import json

import logging
import collections

from urllib.parse import quote, unquote

from .. import common
from . import maps
from . import domains

log = logging.getLogger('ipsl')


def _parse_protocols(**kw):
    protocol_info = collections.OrderedDict()
    for protocol in common.protocols:
        address = kw.get(protocol)
        if address is None:
            continue

        address = common.utils.clean_address(protocol, address)
        domain = address.split('/')[0]
        address = quote(address, safe='')

        protocol_info[protocol] = {
            'address': address,
            'domain': domain,
        }
    return protocol_info


def _get_ipfs_address(protocol_info, _map):
    for protocol, info in protocol_info.items():
        if protocol == 'ipfs':
            ipfs_address = info['address']
            return ipfs_address

        protocol_entries = _map.get(protocol)
        if protocol_entries is None:
            continue

        protocol_links = protocol_entries.get(info['address'])
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
    protocol_info = _parse_protocols(ipfs=ipfs, https=https, ftp=ftp)
    if len(protocol_info) < 1:
        return maps.get(quiet=quiet)

    log.debug("Protocol addresses:\n%s", protocol_info)

    _map = maps.get()
    ipfs_address = _get_ipfs_address(protocol_info, _map)
    _links = _get_ipfs_links(ipfs_address, _map)
    if _links is None:
        return

    _links['ipfs'] = ipfs_address
    _links = {protocol: unquote(address) for protocol, address in _links.items()}

    if not quiet:
        links_str = json.dumps(_links, indent=4, sort_keys=True)
        print(links_str)
    return _links


def _add_ipfs_entry(_map, protocol_info):
    location_protocols_mapping = {
        _protocol: info['address']
        for _protocol, info in protocol_info.items()
        if _protocol != 'ipfs'
    }
    entry = {protocol_info['ipfs']['address']: location_protocols_mapping}
    _map['ipfs'].update(entry)
    return _map


def _add_protocol_entries(_map, protocol_info):
    _map = _add_ipfs_entry(_map, protocol_info)
    for protocol, info in protocol_info.items():
        if protocol == 'ipfs':
            continue
        entry = {info['address']: {'ipfs': protocol_info['ipfs']['address']}}
        _map[protocol].update(entry)
    return _map


def _strip_domains(protocol_info):
    all_domains = set()
    for protocols, info in protocol_info.items():
        if protocols == 'ipfs':
            continue
        all_domains.add(info['domain'])
    return all_domains


def add(ipfs=None, https=None, ftp=None, **_):
    log.debug("Add links")
    protocol_info = _parse_protocols(ipfs=ipfs, https=https, ftp=ftp)
    assert 'ipfs' in protocol_info
    if len(protocol_info) < 2:
        raise ValueError("At least two protocol addresses required")
    log.debug("Protocol addresses:\n%s", protocol_info)

    _map = maps.get()
    _map = _add_protocol_entries(_map, protocol_info)
    maps.put(_map)

    for domain in _strip_domains(protocol_info):
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
