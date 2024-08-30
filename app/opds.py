# -*- coding: utf-8 -*-

"""library opds functions"""

import json
import urllib

from functools import cmp_to_key
from flask import current_app

# pylint: disable=E0402,C0209,C0103
from .internals import get_dtiso, id2path, html_refine, get_genre_name, sizeof_fmt
from .internals import get_book_link
from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_cmp, pubinfo_anno
from .consts import URL, OPDS, LANG, cover_names


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


def str_list(params, layout=None, sub=None):  # pylint: disable=R0914
    """list to opds data struct"""
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

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    if sub is not None:
        workfile = rootdir + idx.replace("/opds", "").replace("rnd-", "") + ".json"
    else:
        workdir = rootdir + idx.replace("/opds", "").replace("rnd-", "")
        workfile = workdir + "/index.json"
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)
    except Exception as e:  # pylint: disable=W0703
        print(e)
        return ret

    data_sorted = []
    if layout == "values":
        for k, v in sorted(data.items(), key=lambda item: item[1]):  # pylint: disable=W0612
            data_sorted.append(k)
    else:
        data_sorted = custom_alphabet_sort(data)

    for d in data_sorted:
        if layout == "values":
            title = data[d]
        else:
            title = d
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d),
                "title": title,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + title + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(d),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def strnum_list(params):  # pylint: disable=R0914
    """list with numbers to opds data struct"""
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

    if params["idxroot"] is None:
        workdir = rootdir + idx.replace("/opds", "")
        workfile = workdir + "/index.json"
    else:
        workdir = rootdir + upref.replace("/opds", "")
        if params["idxroot"] == "":
            workfile = workdir + "/" + params["sub"] + ".json"
        else:
            workfile = workdir + params["idxroot"] + "/" + params["sub"] + ".json"
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        print(e)
        return ret
    # data_sorted = data  # use sort from datachew

    data_middle = []
    for k in sorted(data.keys(), key=cmp_to_key(custom_alphabet_cmp)):
        data_middle.append({"id": k, "name": data[k]})

    if layout != "simple":
        data_sorted = sorted(data_middle, key=cmp_to_key(custom_alphabet_name_cmp))
    else:
        data_sorted = data_middle

    for d in data_sorted:
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(d["id"])
            linetitle = d["id"]
            text = tpl % d["name"]
        else:
            href = approot + baseref + urllib.parse.quote(id2path(d["id"]))
            linetitle = d["name"]
            text = tpl % d["name"]

        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d["id"]),
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


def make_seq_entry(seq, dtiso, subtag, authref, baseref, layout=None, clean_tpl=None):
    name = seq["name"]
    id = seq["id"]
    cnt = seq["cnt"]

    tpl = LANG["books_num"]
    approot = current_app.config['APPLICATION_ROOT']
    if layout == "simple":
        href = approot + baseref + urllib.parse.quote(id)
    else:
        href = approot + baseref + urllib.parse.quote(id2path(id))

    if clean_tpl is None:
        text = tpl % cnt
    else:
        text = ""

    ret = {
        "updated": dtiso,
        "id": subtag + urllib.parse.quote(id),
        "title": name,
        "content": {
            "@type": "text",
            "#text": text
        },
        "link": {
            "@href": href,
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    }
    return ret


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

    for rel in cover_names:
        links.append({
            "@href": "%s/cover/%s/jpg" % (approot, book_id),
            "@rel": rel,
            "@type": "image/jpeg"  # To Do get from db
        })

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


def get_seq_link(approot: str, seqref: str, seq_id: str, seq_name: str):
    """create sequence link for opds"""
    ret = {
        "@href": approot + seqref + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret
