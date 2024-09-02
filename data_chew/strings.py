# -*- coding: utf-8 -*-
"""some string and near-string functions"""

import codecs
import unicodedata as ud
import typing

# pylint: disable=C0103


def strnull(string: typing.Optional[str] = None) -> str:
    """return empty string if None, else return content"""
    if string is None:
        return ""
    return str(string)


def unicode_upper(string: str) -> str:
    """custom UPPER + normalize for sqlite and other"""
    ret = ud.normalize('NFKD', string)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def strlist(string) -> str:
    """return string or first element of list"""
    if isinstance(string, str):
        return strnull(string)
    if isinstance(string, list):
        return strnull(string[0])
    return strnull(str(string))


def strip_quotes(string: str) -> str:
    """
    '"word word"' -> 'word word'
    '"word" word' -> '`word` word'
    """
    if string is None:
        return None
    string = string.replace('"', '`').replace('«', '`').replace('»', '`')
    tmp = string.strip('`')
    if tmp.find('`') == -1:  # not found
        string = tmp
    return string


def quote_string(string: str, errors: str = "strict") -> str:
    """quote string for sql"""
    if string is None:
        return None
    encodable = string.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", str(replacement))

    # OLD return "\"" + encodable.replace("\"", "\"\"") + "\""
    return encodable.replace("\'", "\'\'")


def id2path(id: str):  # pylint: disable=W0622
    """1a2b3c.... to 1a/2b/1a2b3c..."""
    first = id[:2]
    second = id[2:4]
    return first + "/" + second + "/" + id


def id2pathonly(id: str):  # pylint: disable=W0622
    """1a2b3c.... to 1a/2b"""
    first = id[:2]
    second = id[2:4]
    return first + "/" + second
