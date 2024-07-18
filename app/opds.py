# -*- coding: utf-8 -*-

"""library opds functions"""

import json
import urllib

# from functools import cmp_to_key
from flask import current_app

# pylint: disable=E0402,C0209
from .internals import get_dtiso, id2path, html_refine, get_genre_name, sizeof_fmt, url_str
# , get_book_entry, get_seq_link
# from .internals import get_book_link, get_books_descr, get_books_authors
# from .internals import get_books_seqs
# from .internals import unicode_upper, pubinfo_anno
# from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_book_title_cmp
from .internals import custom_alphabet_sort, pubinfo_anno
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
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

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
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

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
    data_sorted = sorted(data.items(), key=lambda x:x[1])
    for d in data_sorted:
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(d[0])
            linetitle = d[0]
            text = tpl % data[d[0]]
        else:
            href = approot + baseref + urllib.parse.quote(id2path(d[0]))
            linetitle = data[d[0]]
            text = tpl % data[d[0]]

        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d[0]),
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


def add_link(data, href, rel, typ):
    data["feed"]["link"].append(
        {
            "@href": href,
            "@rel": rel,
            "@type": typ
        }
    )
    return data


def make_book_entry(book, dtiso, authref, seqref, seq_id=None):
    approot = current_app.config['APPLICATION_ROOT']
    # rootdir = current_app.config['STATIC']
    book_title = book["book_title"]
    book_id = book["book_id"]
    lang = book["lang"]
    annotation = html_refine(book["annotation"])
    size = int(book["size"])
    date_time = book["date_time"]
    zipfile = book["zipfile"]
    filename = book["filename"]
    genres = book["genres"]
    pubinfo = ""
    if "pub_info" in book and book["pub_info"] is not None:
        pubinfo = pubinfo_anno(book["pub_info"])
    authors = []
    links = []
    category = []
    seq_name = ""
    seq_num = ""
    for author in book["authors"]:
        authors.append(
            {
                "uri": approot + authref + id2path(author["id"]),
                "name": author["name"]
            }
        )
        links.append(
            {
                "@href": approot + authref + id2path(author["id"]),
                "@rel": "related",
                "@title": author["name"],
                "@type": "application/atom+xml"
            }
        )
    for gen in genres:
        category.append(
            {
                "@label": get_genre_name(gen),
                "@term": gen
            }
        )
    if book["sequences"] is not None and book["sequences"] != '-':
        for seq in book["sequences"]:
            s_id = seq.get("id")
            if s_id is not None:
                links.append(get_seq_link(approot, seqref, id2path(s_id), seq["name"]))
                if seq_id is not None and seq_id == s_id:
                    seq_name = seq["name"]
                    seq_num = seq.get("num")
                    if seq_num is None:
                        seq_num = "0"
    links.append(get_book_link(approot, zipfile, filename, 'dl'))
    links.append(get_book_link(approot, zipfile, filename, 'read'))

    if seq_id is not None and seq_id != '':
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>Серия: %s, номер: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
    else:
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>
        """ % (annotation, sizeof_fmt(size))
    annotext = annotext + pubinfo
    ret = {
        "updated": date_time,
        "id": "tag:book:" + book_id,
        "title": book_title,
        "author": authors,
        "link": links,
        "category": category,
        "dc:language": lang,
        "dc:format": "fb2",
        "content": {
            "@type": "text/html",
            "#text": annotext
        }
    }
    return ret


def get_book_link(approot: str, zipfile: str, filename: str, ctype: str):
    """create download/read link for opds"""
    title = "Читать онлайн"
    book_ctype = "text/html"
    rel = "alternate"
    if zipfile.endswith('zip'):
        zipfile = zipfile[:-4]
    href = approot + URL["read"] + zipfile + "/" + url_str(filename)
    if ctype == 'dl':
        title = "Скачать"
        book_ctype = "application/fb2+zip"
        rel = "http://opds-spec.org/acquisition/open-access"
        href = approot + URL["dl"] + zipfile + "/" + url_str(filename) + ".zip"
    ret = {
        "@href": href,
        "@rel": rel,
        "@title": title,
        "@type": book_ctype
    }
    return ret


def get_seq_link(approot: str, seqref: str, seq_id: str, seq_name: str):
    """create sequence link for opds"""
    ret = {
        "@href": approot + seqref + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret
