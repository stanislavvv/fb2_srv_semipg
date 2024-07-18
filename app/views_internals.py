# -*- coding: utf-8 -*-
"""library internal functions for opds/html views"""

# from flask import request

# pylint: disable=E0402,C0209
from .opds import main_opds, str_list, strnum_list
from .opds_auth import auth_main, auth_books
# , seq_cnt_list, books_list, auth_list, main_author
# from .opds import author_seqs, name_list, name_cnt_list, random_data
# from .opds import search_main, search_term
from .validate import validate_prefix, validate_id
# , validate_genre_meta
# from .validate import validate_genre, validate_search
# from .internals import id2path, get_author_name, get_seq_name, get_meta_name
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


def view_auth_sub(sub):
    sub = validate_prefix(sub)
    params = {
        "sub": sub,
        "self": URL["authidx"] + sub,
        "upref": URL["authidx"],
        "tag": "tag:authors:" + sub,
        "title": LANG["auth_root_subtitle"] + " '" + sub + "'",
        "subtag": "tag:authors:",
        "subtitle": LANG["auth_root_subtitle"],
        "req": "auth_3"
    }
    if len(sub) >= 3:
        params["baseref"] = URL["author"]
        params["layout"] = "from_id"
        params["tpl"] = LANG["author_tpl"]
        params["idxroot"] = sub[0]
    else:
        params["baseref"] = URL["authidx"]
        params["layout"] = "simple"
        params["tpl"] = LANG["authors_num"]
        params["idxroot"] = None
    return strnum_list(params)


def view_author(sub1, sub2, auth_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)

    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "self": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "upref": URL["authidx"],
        "tag": "tag:root:author:" + auth_id,
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"]
    }
    return auth_main(params)


def view_author_alphabet(sub1, sub2, auth_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "self": URL["author"] + "%s/%s/%s/alphabet" % (sub1, sub2, auth_id),
        "upref": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "tag": "tag:root:author:" + auth_id + ":alphabet",
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "alphabet"
    }
    return auth_books(params)


def view_author_time(sub1, sub2, auth_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "self": URL["author"] + "%s/%s/%s/time" % (sub1, sub2, auth_id),
        "upref": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "tag": "tag:root:author:" + auth_id + ":time",
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "time"
    }
    return auth_books(params)


def view_author_seqs(sub1, sub2, auth_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "self": URL["author"] + "%s/%s/%s/sequences" % (sub1, sub2, auth_id),
        "upref": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "tag": "tag:root:author:" + auth_id + ":sequences",
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequences"
    }
    return auth_books(params)


def view_author_seq(sub1, sub2, auth_id, seq_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "seq_id": seq_id,
        "self": URL["author"] + "%s/%s/%s/%s" % (sub1, sub2, auth_id, seq_id),
        "upref": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "tag": "tag:root:author:" + auth_id + ":sequence:" + seq_id,
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequence"
    }
    return auth_books(params)


def view_author_nonseq(sub1, sub2, auth_id):
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    auth_id = validate_id(auth_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": auth_id,
        "self": URL["author"] + "%s/%s/%s/sequences" % (sub1, sub2, auth_id),
        "upref": URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id),
        "tag": "tag:root:author:" + auth_id + ":sequences",
        "title": LANG["author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequenceless"
    }
    return auth_books(params)

