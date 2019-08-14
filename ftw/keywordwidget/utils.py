from binascii import b2a_qp


def safe_utf8(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    return text


def as_keyword_token(value):
    value = safe_utf8(value)
    return b2a_qp(value)
