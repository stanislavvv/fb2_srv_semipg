# -*- coding: utf-8 -*-
"""library opds functions for authors pages"""

import json

from flask import current_app
from functools import cmp_to_key

from .consts import URL
from .internals import get_dtiso, id2path, custom_alphabet_book_title_cmp, unicode_upper
from .opds import ret_hdr, add_link, make_book_entry


def auth_main(params):
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
            auth_name = "'" + auth_data["name"] + "'"
    except Exception as e:
        print(e)
        auth_name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + auth_name
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


def auth_books(params):
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
    # auth_id = params["id"]

    workdir = rootdir + self.replace("/opds", "")
    workfile = workdir + "/index.json"
    try:
        with open(workfile) as nm:
            auth_data = json.load(nm)
            auth_name = "'" + auth_data["name"] + "'"
    except Exception as e:
        print(e)
        auth_name = ""

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + auth_name
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    workfile = workdir + "/all.json"
    data = []
    try:
        with open(workfile) as nm:
            data = json.load(nm)
    except Exception as e:
        print(e)
        return ret
    if layout == "alphabet":
        data = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))
    if layout == "time":
        data = sorted(data, key=lambda s: unicode_upper(s["date_time"]))
    for book in data:
        ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref))
    return ret
