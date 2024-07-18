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
    # subtitle = params["subtitle"]
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
