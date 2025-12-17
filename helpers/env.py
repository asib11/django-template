import os


_enabled_values = (
    't',
    'true',
    'T',
    'True',
    'TRUE'
)


def is_enabled(key: str):
    value: str = os.environ.get(key) or ''
    value = value.lower()
    return value in _enabled_values



def get_items(key: str, splitter=',') -> list:
    values = os.getenv(key=key) or ''
    result = values.split(splitter)
    return result




