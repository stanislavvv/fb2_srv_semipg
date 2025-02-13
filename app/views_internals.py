# -*- coding: utf-8 -*-
"""library internal functions for opds/html views"""

from flask import request

# pylint: disable=E0402,C0209
from .opds import main_opds, str_list, strnum_list
from .opds_auth import auth_main, auth_books
from .opds_seq import seq_books
from .opds_gen import genre_books, rnd_genre_books
from .opds_search import search_main, search_term, random_books, random_seqs, books_global_by_time
from .validate import validate_prefix, validate_id, validate_genre_meta
from .validate import validate_genre, validate_search, redir_invalid
from .internals import get_meta_name, get_genre_name
from .consts import LANG, URL

REDIR_ALL = "html.html_root"


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
    """authorsindes/<sub>"""
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
    """author/sub1/sub2/id"""
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
        "title": LANG["author_tpl"],
        "authref": URL["author"],
        "seqref": URL["seq"]
    }
    return auth_main(params)


def view_author_alphabet(sub1, sub2, auth_id):
    """author/sub1/sub2/id/alphabet"""
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
        "title": LANG["books_author_alphabet"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "alphabet"
    }
    return auth_books(params)


def view_author_time(sub1, sub2, auth_id):
    """author/sub1/sub2/id/time"""
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
        "title": LANG["books_author_time"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "time"
    }
    return auth_books(params)


def view_author_seqs(sub1, sub2, auth_id):
    """author/sub1/sub2/id/sequences"""
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
        "title": LANG["seqs_author"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequences"
    }
    return auth_books(params)


def view_author_seq(sub1, sub2, auth_id, seq_id):
    """author/sub1/sub2/id/seq_id"""
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
        "title": LANG["books_author_seq"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequence"
    }
    return auth_books(params)


def view_author_nonseq(sub1, sub2, auth_id):
    """author/sub1/sub2/id/sequenceless"""
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
        "title": LANG["books_author_nonseq"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequenceless"
    }
    return auth_books(params)


def view_seq_root():
    """sequencesindex/"""
    params = {
        "self": URL["seqidx"],
        "baseref": URL["seqidx"],
        "upref": URL["start"],
        "tag": "tag:root:sequences",
        "title": LANG["sequences"],
        "subtag": "tag:sequences:",
        "subtitle": LANG["seq_root_subtitle"],
        "req": "seq_1"
    }
    return str_list(params)


def view_seq_sub(sub):
    """sequencesindex/sub"""
    sub = validate_prefix(sub)
    params = {
        "sub": sub,
        "self": URL["seqidx"] + sub,
        "upref": URL["seqidx"],
        "tag": "tag:sequences:" + sub,
        "title": LANG["seq_root_subtitle"] + " '" + sub + "'",
        "subtag": "tag:sequences:",
        "subtitle": LANG["seq_root_subtitle"],
        "req": "seq_3"
    }
    if len(sub) >= 3:
        params["baseref"] = URL["seq"]
        params["layout"] = "from_id"
        params["tpl"] = LANG["seq_tpl"]
        params["idxroot"] = sub[0]
    else:
        params["baseref"] = URL["seqidx"]
        params["layout"] = "simple"
        params["tpl"] = LANG["seqs_num"]
        params["idxroot"] = None
    return strnum_list(params)


def view_seq(sub1, sub2, seq_id):
    """sequence/sub1/sub2/id"""
    sub1 = validate_prefix(sub1)
    sub2 = validate_prefix(sub2)
    seq_id = validate_id(seq_id)
    params = {
        "sub1": sub1,
        "sub2": sub2,
        "id": seq_id,
        "self": URL["seq"] + "%s/%s/%s" % (sub1, sub2, seq_id),
        "upref": URL["seq"] + "%s/%s/%s" % (sub1, sub2, seq_id),
        "tag": "tag:root:sequence:" + seq_id,
        "title": LANG["sequence"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "layout": "sequence"
    }
    return seq_books(params)


def view_gen_root():
    """genresindex/"""
    params = {
        "self": URL["genidx"],
        "baseref": URL["genidx"],
        "upref": URL["start"],
        "tag": "tag:root:genres",
        "title": LANG["genres_meta"],
        "subtag": "tag:genres:",
        "subtitle": LANG["genres_root_subtitle"]
    }
    return str_list(params, layout="values")


def view_gen_meta(sub):
    """genresindex/sub"""
    sub = validate_genre_meta(sub)
    meta_name = get_meta_name(sub)
    if meta_name is not None:
        params = {
            "self": URL["genidx"] + sub,
            "baseref": URL["genre"],
            "upref": URL["genidx"],
            "tag": "tag:genres:" + sub,
            "title": LANG["genres_root_subtitle"] + "'" + meta_name + "'",
            "subtag": "tag:genres:",
            "subtitle": LANG["genres_root_subtitle"]
        }
        return str_list(params, layout="values", sub=sub)
    return redir_invalid(REDIR_ALL)


def view_genre(gen_id, page):
    """genre/id/page"""
    gen_id = validate_genre(gen_id)
    gen_name = get_genre_name(gen_id)
    params = {
        "id": gen_id,
        "self": URL["genre"] + "%s" % gen_id,
        "upref": URL["genidx"],
        "tag": "tag:root:genre:" + gen_id,
        "title": LANG["genre_tpl"] % gen_name,
        "authref": URL["author"],
        "seqref": URL["seq"],
        "name": gen_name,
        "page": page
    }
    return genre_books(params)


def view_search():
    """main search page data"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    self = URL["search"]
    upref = URL["start"]
    tag = "tag:search::"
    title = LANG["search_main"] % s_term
    data = search_main(s_term, tag, title, self, upref)
    return data


def view_search_term(direction):
    """genre/id/page"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    params = {
        "search_term": s_term,
        "upref": URL["start"],
        "authref": URL["author"],
        "seqref": URL["seq"]
    }
    if direction == "byauthor":
        params["self"] = URL["srchauth"]
        params["tag"] = "tag:search:authors:"
        params["subtag"] = "tag:author:"
        params["baseref"] = URL["author"]
        params["title"] = LANG["search_author"] % s_term
        params["restype"] = "auth"
    elif direction == "bysequence":
        params["self"] = URL["srchseq"]
        params["tag"] = "tag:search:sequences:"
        params["subtag"] = "tag:sequence:"
        params["baseref"] = URL["seq"]
        params["title"] = LANG["search_seq"] % s_term
        params["restype"] = "seq"
    elif direction == "bytitle":
        params["self"] = URL["srchbook"]
        params["tag"] = "tag:search:books:"
        params["subtag"] = "tag:book:"
        params["baseref"] = URL["author"]
        params["title"] = LANG["search_book"] % s_term
        params["restype"] = "book"
    else:  # annotation by default
        params["self"] = URL["srchbook"]
        params["tag"] = "tag:search:books:"
        params["subtag"] = "tag:book:"
        params["baseref"] = URL["author"]
        params["title"] = LANG["search_anno"] % s_term
        params["restype"] = "bookanno"
    return search_term(params)


def view_random_books():
    """random books"""
    params = {
        "self": URL["rndbook"],
        "upref": URL["start"],
        "tag": "tag:search:books:random:",
        "title": LANG["rnd_books"],
        "authref": URL["author"],
        "seqref": URL["seq"]
    }
    data = random_books(params)
    return data


def view_random_seqs():
    """random sequences"""
    params = {
        "self": URL["rndseq"],
        "upref": URL["start"],
        "tag": "tag:search:sequences:random:",
        "title": LANG["rnd_seqs"],
        "authref": URL["author"],
        "baseref": URL["seq"],
        "subtag": "tag:search:sequence:random:"
    }
    data = random_seqs(params)
    return data


def view_rnd_gen_root():
    """random genresindex/"""
    params = {
        "self": URL["rndgenidx"],
        "baseref": URL["rndgenidx"],
        "upref": URL["rndgenidx"],
        "tag": "tag:rnd:genres",
        "title": LANG["genres_meta"],
        "subtag": "tag:rnd:genres:",
        "subtitle": LANG["genres_root_subtitle"]
    }
    return str_list(params, layout="values")


def view_rnd_gen_meta(sub):
    """random genresindex/sub"""
    sub = validate_genre_meta(sub)
    meta_name = get_meta_name(sub)
    if meta_name is not None:
        params = {
            "self": URL["rndgenidx"] + sub,
            "baseref": URL["rndgen"],
            "upref": URL["rndgenidx"],
            "tag": "tag:rnd:genres:" + sub,
            "title": LANG["genres_root_subtitle"] + "'" + meta_name + "'",
            "subtag": "tag:rnd:genres:",
            "subtitle": LANG["genres_root_subtitle"]
        }
        return str_list(params, layout="values", sub=sub)
    return redir_invalid(REDIR_ALL)


def view_rnd_genre(gen_id):
    """random genre/id"""
    gen_id = validate_genre(gen_id)
    gen_name = get_genre_name(gen_id)
    params = {
        "id": gen_id,
        "self": URL["rndgen"] + "%s" % gen_id,
        "upref": URL["rndgenidx"],
        "tag": "tag:rnd:genre:" + gen_id,
        "title": LANG["rnd_genre_books"] % gen_name,
        "authref": URL["author"],
        "seqref": URL["seq"],
        "name": gen_name
    }
    return rnd_genre_books(params)


def view_time(page=0):
    params = {
        "self": URL["time"],
        "tag": "tag:root:books:time",
        "upref": URL["start"],
        "title": LANG["all_books_by_time"],
        "authref": URL["author"],
        "seqref": URL["seq"],
        "page": page
    }
    return books_global_by_time(params)
