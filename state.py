
_enter_text = False


def check_state():
    return not _enter_text


def start_enter_text():
    global _enter_text
    _enter_text = True


def finish_enter_text():
    global _enter_text
    _enter_text = False
