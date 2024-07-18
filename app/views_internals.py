# -*- coding: utf-8 -*-
"""library internal functions for opds/html views"""

# from flask import request

# pylint: disable=E0402,C0209
from .opds import main_opds, str_list  # , seq_cnt_list, books_list, auth_list, main_author
# from .opds import author_seqs, name_list, name_cnt_list, random_data
# from .opds import search_main, search_term
# from .validate import validate_prefix, validate_id, validate_genre_meta
# from .validate import validate_genre, validate_search
# from .internals import id2path, get_author_name, get_seq_name, get_meta_name, get_genre_name
from .consts import LANG, URL


def view_main():
    """root"""
    return main_opds()


def view_auth_root():
    """authorsindex/"""
    params = {
        "self": URL["authidx"],
        "baseref": URL["authidx"],
        "upref": URL["start"],
        "tag": "tag:root:authors",
        "title": LANG["authors"],
        "subtag": "tag:authors:",
        "subtitle": LANG["auth_root_subtitle"],
        "req": "auth_1"
    }
    return str_list(params)
