# -*- coding: utf-8 -*-
"""library opds functions for authors pages"""

import json

from functools import cmp_to_key
from flask import current_app

from .consts import URL
from .internals import get_dtiso, custom_alphabet_book_title_cmp
from .opds import ret_hdr, add_link, make_book_entry

# pylint: disable=C0103


def genre_books(params):  # pylint: disable=R0914
    """make data for genre's books"""
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    self = params["self"]
    title = params["title"]
    tag = params["tag"]
    upref = params["upref"]
    authref = params["authref"]
    seqref = params["seqref"]
    gen_id = params["id"]
    page = params["page"]

    workdir = rootdir + URL["genre"].replace("/opds", "") + gen_id + "/"
    workfile = workdir + str(page) + ".json"

    books = []
    try:
        with open(workfile) as nm:
            books = json.load(nm)
    except Exception as e:  # pylint: disable=W0703
        print(e)

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    prev_page = page - 1
    next_page = page + 1
    if prev_page > 0:
        ret["feed"]["link"].append(
            {
                "@href": approot + self + "/" + str(prev_page),
                "@rel": "prev",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    if prev_page == 0:
        ret["feed"]["link"].append(
            {
                "@href": approot + self,
                "@rel": "prev",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    ret["feed"]["link"].append(
        {
            "@href": approot + self + "/" + str(next_page),
            "@rel": "next",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = sorted(books, key=cmp_to_key(custom_alphabet_book_title_cmp))
    for book in data:
        ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref))
    return ret
