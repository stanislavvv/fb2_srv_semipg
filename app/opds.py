# -*- coding: utf-8 -*-

"""library opds functions"""

import json
# import logging
# import urllib

# from functools import cmp_to_key
from flask import current_app

# pylint: disable=E0402,C0209
from .internals import get_dtiso  # , id2path, get_book_entry, sizeof_fmt, get_seq_link
# from .internals import get_book_link, url_str, get_books_descr, get_books_authors
# from .internals import get_books_seqs, get_genre_name
# from .internals import unicode_upper, html_refine, pubinfo_anno
# from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_book_title_cmp
from .consts import URL, OPDS  # ,cover_names

# from .opds_int import ret_hdr

# from .db import dbconnect, quote_string


def main_opds():
    """return opds root struct"""
    approot = current_app.config['APPLICATION_ROOT']
    dtiso = get_dtiso()

    # start data
    data = OPDS["main"] % (
        dtiso, approot, URL["search"],
        approot, URL["start"],  # start
        approot, URL["start"],  # self
        dtiso, approot, URL["time"],
        dtiso, approot, URL["authidx"],
        dtiso, approot, URL["seqidx"],
        dtiso, approot, URL["genidx"],
        dtiso, approot, URL["rndbook"],
        dtiso, approot, URL["rndseq"],
        dtiso, approot, URL["rndgenidx"]
    )
    return json.loads(data)
