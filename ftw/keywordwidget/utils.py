def safe_utf8(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    return text
