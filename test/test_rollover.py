import pytest
import builtins
import time

builtins.phones = {}
builtins.resolved_devs = []
builtins.resolved_macs = []


class Args:
    ttl = 5e10


builtins.args = Args()

from rollover import *

MAC = 'ab:cd:de:ad:be:ef'
NEWMAC = 'aa:aa:aa:aa:aa:aa'
DEV = {
    'alias': 'device_alias',
    'time': int(time.time()),
    'device': 'Watch',
    'os': 'WatchOS',
}


def test_builtins():
    assert type(phones) == dict


@pytest.mark.parametrize(
    'mac,dev,seq,xres',
    [
        [MAC, {}, None, None],
        [MAC, {'device': '<unknown>', 'os': 'WatchOS'}, 0xabcd, None],
        [MAC, {'device': 'Watch', 'os': '<unknown>'}, 0xabcd, None],
    ],
)
def test_get_or_assign_alias(mac, dev, seq, xres):
    phones[mac] = dev
    assert get_or_assign_alias(mac, seq) == xres


def update_rollover(rd, nv):
    for key in list(rd):
        if key in nv:
            rd[key] = nv[key]
        else:
            rd.pop(key)


def test_assign_alias():
    assert get_alias(MAC, '1100') is not None


@pytest.mark.parametrize(
    'mac,MR,dev,xres', [[MAC, {}, DEV, None], [MAC, {MAC: DEV}, DEV, DEV['alias']]]
)
def test_mac_rollover(mac, MR, dev, xres):
    phones[mac] = dev
    update_rollover(MAC_ROLLOVER, MR)
    assert mac_rollover(mac) == xres
    assert mac in MAC_ROLLOVER


@pytest.mark.parametrize(
    'mac,seq,seq2,SR,dev,xrollover',
    [
        [MAC, None, None, {}, DEV, False],
        [MAC, '1000', '1100', {}, DEV, True],
        [MAC, '1000', '1100', {'00': DEV}, DEV, True],
    ],
)
def test_seq_rollover(mac, seq, seq2, SR, dev, xrollover):
    phones[mac] = dev
    update_rollover(SEQ_ROLLOVER, SR)

    if seq is None:
        return

    seq_base, seq_iter, ident = get_ident(mac, seq)

    # MAC rotates
    if seq2 is not None:
        phones[NEWMAC] = dev
        assert (seq_rollover(NEWMAC, seq2) == dev['alias']) == xrollover


@pytest.mark.parametrize(
    'mac,newmac,seq,dev', [[MAC, NEWMAC, '1000', DEV], [MAC, NEWMAC, '1000', DEV]]
)
def test_rollover(mac, newmac, seq, dev):
    alias = mac_rollover(mac) or seq_rollover(mac, seq) or get_alias(mac, seq)
    assert alias is not None
    assert (
        mac_rollover(newmac) or seq_rollover(newmac, seq) or get_alias(newmac, seq)
    ) == alias

