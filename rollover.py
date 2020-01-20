import time
import re
import logging

SEQ_ROLLOVER = {}
MAC_ROLLOVER = {}

LOG = logging.getLogger(__name__)
# LOG.setLevel(logging.DEBUG)
# LOG.addHandler(logging.FileHandler('rollover.log'))


def clean_rollover(rollover):
    for ident in list(rollover.keys()):
        details = rollover[ident]
        cur_time = int(time.time())
        if cur_time - details["time"] > args.ttl:
            rollover.pop(ident)


def get_ident(mac, seq):
    seq_base = seq[2:]
    seq_iter = int(seq[:2], base=16)
    ident = (phones[mac]["device"], phones[mac]["os"], seq_base)
    return seq_base, seq_iter, ident


def get_alias(mac, seq):
    return re.sub(' ', '_', '_'.join([phones[mac]["device"], phones[mac]["os"], seq]))


def seq_rollover(mac, seq):
    if seq is None:
        return

    seq_base, seq_iter, ident = get_ident(mac, seq)

    # clean_rollover(SEQ_ROLLOVER)
    alias = None

    # Attempt to find a seq rollover candidate
    for candidate, details in SEQ_ROLLOVER.items():
        if (
            phones[mac]["device"] == candidate[0]
            and phones[mac]["os"] == candidate[1]
            and seq_base == candidate[2]
        ):
            alias = details["alias"]

    SEQ_ROLLOVER[ident] = phones[mac]
    return alias


def mac_rollover(mac):
    # clean_rollover(MAC_ROLLOVER)

    if mac in MAC_ROLLOVER:
        return MAC_ROLLOVER[mac]["alias"]
    else:
        MAC_ROLLOVER[mac] = phones[mac]


def get_or_assign_alias(mac, seq):
    if seq is None:
        return
    if 'unknown' in phones[mac]["device"] or 'unknown' in phones[mac]["os"]:
        return
    if 'error' in phones[mac]["device"] or 'error' in phones[mac]["os"]:
        return
    if 'iOS10' in phones[mac]['os']:
        # likely a watch that hasn't booted up yet
        return

    alias = mac_rollover(mac) or seq_rollover(mac, seq) or get_alias(mac, seq)
    rollover = alias != phones[mac]['alias']
    LOG.debug(f'{mac}, {seq} => {alias}, {rollover}')
    return alias


def correlate_devices():
    for mac in list(phones.keys()):
        try:
            phones[mac]['alias'] = get_or_assign_alias(
                mac, phones[mac].get('seq', None)
            )
        except KeyError:
            # just accept the race condition and move on
            pass

