
_hold_ids = set()


def check_state(cid):
    return cid not in _hold_ids


def start_enter_text(cid):
    global _hold_ids
    _hold_ids.add(cid)


def finish_enter_text(cid):
    global _hold_ids
    _hold_ids.remove(cid)
