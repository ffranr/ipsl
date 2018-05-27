import time
import decimal
import logging
import subprocess

import cbor2 as cbor
import simplejson as json
import ipfsapi

log = logging.getLogger('ipg')

_daemon_ip = '127.0.0.1'
_daemon_port = 5001
start_daemon_sleep = 4


def connect():
    try:
        ipfs_api = ipfsapi.connect(_daemon_ip, _daemon_port)
    except ipfsapi.exceptions.ConnectionError:
        ipfs_api = _start_daemon_connect()
    else:
        log.debug('Connected to IPFS daemon')
    ipfs_api.dag_put = _dag_put
    ipfs_api.dag_get = _dag_get
    ipfs_api.local_peer_id = _local_peer_id
    return ipfs_api


def _start_daemon_connect():
    log.debug('Starting IPFS daemon')
    subprocess.Popen(['ipfs', 'daemon'])
    time.sleep(start_daemon_sleep)

    try:
        ipfs_api = ipfsapi.connect(_daemon_ip, _daemon_port)
    except ipfsapi.exceptions.ConnectionError:
        log.error('Connecting to IPFS daemon failed')
        exit(1)
    else:
        log.debug('Connected to IPFS daemon')
        return ipfs_api


def _dag_put(dag):
    dag = cbor.dumps(dag)
    command = ["ipfs", "dag", "put", "--pin", "--input-enc=raw"]
    stdout = subprocess.check_output(command, input=dag)
    cid = stdout.decode("utf-8")
    cid = cid.rstrip("\n")
    return cid


def _dag_get(cid):
    command = ["ipfs", "dag", "get", cid]
    stdout = subprocess.check_output(command)
    stdout = stdout.decode("utf-8")
    dag = json.loads(stdout, parse_float=decimal.Decimal)
    return dag


def _local_peer_id():
    ipfs_api = connect()
    result = ipfs_api.id()
    peer_id = result["ID"]
    return peer_id
