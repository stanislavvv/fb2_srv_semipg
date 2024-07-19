# -*- coding: utf-8 -*-
"""library opds functions for seqors pages"""

import json

from flask import current_app

from .consts import URL
from .internals import get_dtiso, id2path
from .opds import ret_hdr, add_link, make_book_entry


def seq_books(params):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    self = params["self"]
    # idx = self.replace("/opds", "")
    title = params["title"]
    tag = params["tag"]
    self = params["self"]
    upref = params["upref"]
    authref = params["authref"]
    seqref = params["seqref"]
    seq_id = params["id"]

    workfile = rootdir + URL["seq"].replace("/opds", "") + id2path(seq_id) + ".json"
    seq_data = {}
    try:
        with open(workfile) as nm:
            seq_data = json.load(nm)
            seq_name = "'" + seq_data["name"] + "'"
    except Exception as e:
        print(e)
        seq_name = ""

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + seq_name
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    data = seq_data["books"]

    data_seq = []

    for book in data:
        if book["sequences"] is not None:
            for s in book["sequences"]:
                if s.get("id") == seq_id:
                    snum = s.get("num")
                    if snum is not None:
                        seq_num = int(snum)
                    book["seq_num"] = seq_num
                    data_seq.append(book)
    data = sorted(data_seq, key=lambda s: s["seq_num"] or -1)

    for book in data:
        ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref, seq_id=seq_id))
    return ret
