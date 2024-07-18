# -*- coding: utf-8 -*-

"""library opds functions"""

import json
import urllib

# from functools import cmp_to_key
from flask import current_app

# pylint: disable=E0402,C0209
from .internals import get_dtiso, id2path  # , get_book_entry, sizeof_fmt, get_seq_link
# from .internals import get_book_link, url_str, get_books_descr, get_books_authors
# from .internals import get_books_seqs, get_genre_name
# from .internals import unicode_upper, html_refine, pubinfo_anno
# from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_book_title_cmp
from .internals import custom_alphabet_sort
from .consts import URL, OPDS

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


def str_list(params):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    idx = params["self"]
    baseref = params["baseref"]
    title = params["title"]
    subtitle = params["subtitle"]
    tag = params["tag"]
    subtag = params["subtag"]
    self = params["self"]
    upref = params["upref"]
    workdir = rootdir + idx.replace("/opds", "")
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    try:
        with open(workdir + "/index.json") as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        print(e)
        return ret
    data_sorted = custom_alphabet_sort(data)
    for d in data_sorted:
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d),
                "title": d,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + d + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(d),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def strnum_list(params):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    idx = params["self"]
    baseref = params["baseref"]
    title = params["title"]
    subtitle = params["subtitle"]
    tag = params["tag"]
    subtag = params["subtag"]
    self = params["self"]
    upref = params["upref"]
    tpl = params["tpl"]
    layout = params["layout"]
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    print(json.dumps(params, indent=2, ensure_ascii=False))
    if params["idxroot"] is not None:
        workdir = rootdir + upref.replace("/opds", "")
        workfile = workdir + params["idxroot"] + "/" + params["sub"] + ".json"
    else:
        workdir = rootdir + idx.replace("/opds", "")
        workfile = workdir + "/index.json"
    print("dir: %s, file: %s" % (workdir, workfile))
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        print(e)
        return ret
    print(json.dumps(data, indent=2, ensure_ascii=False))
    data_sorted = custom_alphabet_sort(data)
    for d in data_sorted:
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(d)
            linetitle = d
            text = tpl % data[d]
        else:
            href = approot + baseref + urllib.parse.quote(id2path(d))
            linetitle = data[d]
            text = tpl % data[d]

        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d),
                "title": linetitle,
                "content": {
                    "@type": "text",
                    # "#text": subtitle + "'" + data[d] + "'"
                    "#text": text
                },
                "link": {
                    "@href": href,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def ret_hdr():  # python does not have constants
    """return opds title"""
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "updated": "0000-00-00_00:00",
            "title": "Books by authors",
            "icon": "/favicon.ico",
            "link": [
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + URL["search"] + "?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + URL["start"],
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }
