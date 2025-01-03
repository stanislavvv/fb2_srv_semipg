# -*- coding: utf-8 -*-
"""library opds functions for authors pages"""

import json

from functools import cmp_to_key
from flask import current_app

from .consts import URL
from .internals import get_dtiso, id2path, custom_alphabet_book_title_cmp, unicode_upper
from .internals import custom_alphabet_name_cmp, get_seq_name
from .opds import ret_hdr, add_link, make_book_entry, make_seq_entry
# pylint: disable=C0103,R1702,R1705,R0912


def auth_main(params):  # pylint: disable=R0914
    """main page for author"""
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    self = params["self"]
    idx = self.replace("/opds", "")
    # baseref = params["baseref"]
    title = params["title"]
    # subtitle = params["subtitle"]
    tag = params["tag"]
    # subtag = params["subtag"]
    self = params["self"]
    upref = params["upref"]
    auth_id = params["id"]

    workfile = rootdir + "/" + idx + "/index.json"
    try:
        with open(workfile) as nm:
            auth_data = json.load(nm)
            auth_name = auth_data["name"]
    except Exception as e:  # pylint: disable=W0703
        print(e)
        auth_name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title % auth_name
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    ret["feed"]["entry"] = [
                {
                    "updated": dtiso,
                    "id": "tag:author:bio:" + auth_id,
                    "title": "Об авторе",
                    "link": [
                        {
                            "@href": approot + URL["author"] + id2path(auth_id) + "/sequences",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Books of author by sequences",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        },
                        {
                            "@href": approot + URL["author"] + id2path(auth_id) + "/sequenceless",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Sequenceless books of author",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    ],
                    "content": {
                        "@type": "text/html",
                        "#text": "<p><span style=\"font-weight:bold\">" + auth_name + "</span></p>"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequences",
                    "title": "По сериям",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequenceless",
                    "title": "Вне серий",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/sequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":alphabet",
                    "title": "По алфавиту",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":time",
                    "title": "По дате добавления",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/time",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]

    return ret


def auth_books(params):  # pylint: disable=R0914,R0915
    """make data for author's books"""
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
    layout = params["layout"]
    auth_id = params["id"]

    # workdir = rootdir + self.replace("/opds", "")
    workdir = rootdir + URL["author"].replace("/opds", "") + id2path(auth_id)
    workfile = workdir + "/index.json"
    try:
        with open(workfile) as nm:
            auth_data = json.load(nm)
            auth_name = auth_data["name"]
    except Exception as e:  # pylint: disable=W0703
        print(e)
        auth_name = ""

    if layout == "sequence":
        seq_name = get_seq_name(params["seq_id"])
        full_title = title % (seq_name, auth_name)
    else:
        full_title = title % auth_name

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = full_title
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    if layout == "sequences":
        workfile = workdir + "/sequences.json"
    else:
        workfile = workdir + "/all.json"
    data = []
    try:
        with open(workfile) as nm:
            data = json.load(nm)
    except Exception as e:  # pylint: disable=W0703
        print(e)
        return ret

    if layout == "time":
        data = sorted(data, key=lambda s: unicode_upper(s["date_time"]))
    elif layout == "alphabet":
        data = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))

    if layout == "sequenceless":
        data_nonseq = []
        for book in data:
            if book["sequences"] is None:
                data_nonseq.append(book)
        data = sorted(data_nonseq, key=cmp_to_key(custom_alphabet_book_title_cmp))

    if layout == "sequences":
        data = sorted(data, key=cmp_to_key(custom_alphabet_name_cmp))
        baseref = upref + "/"
        subtag = "tag:author:" + auth_id + ":sequence:"
        for seq in data:
            ret["feed"]["entry"].append(make_seq_entry(seq, dtiso, subtag, authref, baseref, layout="simple"))
        return ret
    elif layout == "sequence":
        data = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))  # presort unnumbered books
        data_seq = []
        seq_id = params["seq_id"]
        for book in data:
            if book["sequences"] is not None and seq_name is not None:
                for s in book["sequences"]:
                    seq_num = 0
                    if s.get("id") == seq_id:
                        snum = s.get("num")
                        if snum is not None:
                            seq_num = int(snum)
                        book["seq_num"] = seq_num
                        data_seq.append(book)
        data = sorted(data_seq, key=lambda s: s["seq_num"] or -1)

    for book in data:
        if layout == "sequence":
            ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref, seq_id=seq_id))
        else:
            ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref))
    return ret
