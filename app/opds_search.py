# -*- coding: utf-8 -*-
"""library opds functions for authors pages"""

import json
import urllib
import logging

# from functools import cmp_to_key
from flask import current_app

from .consts import URL
from .internals import get_dtiso, url_str, get_books_descr, unicode_upper, id2path
from .opds import ret_hdr, make_book_entry, make_seq_entry, add_link
from .db import dbconnect


def search_main(s_term: str, tag: str, title: str, self: str, upref: str):
    """opds main search page"""
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    if s_term is None:
        ret["feed"]["id"] = tag
    else:
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:authors:",
            "title": "Поиск в именах авторов",
            "content": {
              "@type": "text",
              "#text": "Поиск в именах авторов"
            },
            "link": {
              "@href": approot + URL["srchauth"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:sequences:",
            "title": "Поиск в сериях",
            "content": {
              "@type": "text",
              "#text": "Поиск в сериях"
            },
            "link": {
              "@href": approot + URL["srchseq"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:booktitles:",
            "title": "Поиск в названиях книг",
            "content": {
              "@type": "text",
              "#text": "Поиск в названиях книг"
            },
            "link": {
              "@href": approot + URL["srchbook"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:bookanno:",
            "title": "Поиск в аннотациях книг",
            "content": {
              "@type": "text",
              "#text": "Поиск в аннотациях книг"
            },
            "link": {
              "@href": approot + URL["srchbookanno"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
    return ret


def search_term(params):
    """search function"""
    s_term = params["search_term"]
    self = params["self"]
    baseref = params["baseref"]
    title = params["title"]
    tag = params["tag"]
    subtag = params["subtag"]
    self = params["self"]
    upref = params["upref"]
    authref = params["authref"]
    seqref = params["seqref"]

    restype = params["restype"]

    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    if s_term is None:  # pylint: disable=R1702
        ret["feed"]["id"] = tag
    else:
        s_terms = s_term.split()
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        data = []
        maxres = current_app.config['MAX_SEARCH_RES']
        try:
            db_conn = dbconnect()
            if restype in ("book", "bookanno"):
                book_ids = []
                if restype == "book":
                    dbdata = db_conn.get_search_titles(s_terms, maxres)
                else:
                    dbdata = db_conn.get_search_anno(s_terms, maxres)

                for book in dbdata:
                    book_ids.append(book[0])
                dbdata = db_conn.get_books_byids(book_ids)
                book_descr = get_books_descr(book_ids)

                for book in dbdata:
                    zipfile = book[0]
                    filename = book[1]
                    genres = book[2]
                    author_ids = book[3]
                    seq_ids = book[4]
                    book_id = book[5]
                    lang = book[6]
                    date = str(book[7])
                    size = book[8]
                    deleted = book[9]

                    book_authors_data = db_conn.get_authors(author_ids)
                    authors = []
                    for auth in book_authors_data:
                        authors.append({"id": auth[0], "name": auth[1]})
                    sequences = []
                    if len(seq_ids) > 0:
                        book_seq_data = db_conn.get_seq_names(seq_ids)

                        for seq in book_seq_data:
                            seq_id = seq[0]
                            seq_name = seq[1]
                            sequences.append({"id": seq_id, "name": seq_name})

                    (
                        book_title,
                        pub_isbn,
                        pub_year,
                        publisher,
                        publisher_id,
                        annotation
                    ) = ('---', None, None, None, None, '')
                    if book_id in book_descr:
                        (book_title, pub_isbn, pub_year, publisher, publisher_id, annotation) = book_descr[book_id]
                    data.append({
                        "zipfile": zipfile,
                        "filename": filename,
                        "genres": genres,
                        "authors": authors,
                        "sequences": sequences,
                        "book_title": book_title,
                        "book_id": book_id,
                        "lang": lang,
                        "date_time": date,
                        "size": size,
                        "annotation": annotation,
                        "pub_info": {
                            "isbn": pub_isbn,
                            "year": pub_year,
                            "publisher": publisher,
                            "publisher_id": publisher_id
                        },
                        "deleted": deleted
                    })
            elif restype == "seq":
                dbdata = db_conn.get_search_seqs(s_terms, maxres)
                for seq in dbdata:
                    data.append({
                        "id": seq[0],
                        "name": seq[1],
                        "cnt": 0
                    })
            elif restype == "auth":
                dbdata = db_conn.get_search_authors(s_terms, maxres)
                for auth in dbdata:
                    data.append({
                        "id": auth[0],
                        "name": auth[1]
                    })
            if restype in ("auth", "seq"):
                data = sorted(data, key=lambda s: unicode_upper(s["name"]) or -1)
            elif restype == "book":
                data = sorted(data, key=lambda s: unicode_upper(s["book_title"]) or -1)
        except Exception as ex:  # pylint: disable=W0703
            logging.error(ex)

        print(json.dumps(data, indent=2, ensure_ascii=False))
        for i in data:
            if restype in ("book", "bookanno"):
                ret["feed"]["entry"].append(
                    make_book_entry(i, dtiso, authref, seqref)
                )
            elif restype == "seq":
                ret["feed"]["entry"].append(
                    make_seq_entry(i, dtiso, subtag, authref, baseref)
                )
            elif restype == "auth":
                name = i["name"]
                auth_id = i["id"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(auth_id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": name
                        },
                        "link": {
                            "@href": approot + baseref + id2path(auth_id),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
    return ret


def random_books(params):
    """return random books struct"""
    dtiso = get_dtiso()

    self = params["self"]
    upref = params["upref"]
    tag = params["tag"]
    title = params["title"]
    self = params["self"]
    authref = params["authref"]
    seqref = params["seqref"]

    approot = current_app.config['APPLICATION_ROOT']

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag

    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    try:
        db_conn = dbconnect()
        limit = int(current_app.config['PAGE_SIZE'])
        dbdata = db_conn.get_rnd_books(limit)

        book_ids = []
        for book in dbdata:
            book_ids.append(book[0])

        dbdata = db_conn.get_books_byids(book_ids)
        book_descr = get_books_descr(book_ids)

        data = []
        for book in dbdata:
            zipfile = book[0]
            filename = book[1]
            genres = book[2]
            author_ids = book[3]
            seq_ids = book[4]
            book_id = book[5]
            lang = book[6]
            date = str(book[7])
            size = book[8]
            deleted = book[9]

            book_authors_data = db_conn.get_authors(author_ids)
            authors = []
            for auth in book_authors_data:
                authors.append({"id": auth[0], "name": auth[1]})
            sequences = []
            if len(seq_ids) > 0:
                book_seq_data = db_conn.get_seq_names(seq_ids)

                for seq in book_seq_data:
                    seq_id = seq[0]
                    seq_name = seq[1]
                    sequences.append({"id": seq_id, "name": seq_name})

            (
                book_title,
                pub_isbn,
                pub_year,
                publisher,
                publisher_id,
                annotation
            ) = ('---', None, None, None, None, '')
            if book_id in book_descr:
                (book_title, pub_isbn, pub_year, publisher, publisher_id, annotation) = book_descr[book_id]
            data.append({
                "zipfile": zipfile,
                "filename": filename,
                "genres": genres,
                "authors": authors,
                "sequences": sequences,
                "book_title": book_title,
                "book_id": book_id,
                "lang": lang,
                "date_time": date,
                "size": size,
                "annotation": annotation,
                "pub_info": {
                    "isbn": pub_isbn,
                    "year": pub_year,
                    "publisher": publisher,
                    "publisher_id": publisher_id
                },
                "deleted": deleted
            })

        for i in data:
            ret["feed"]["entry"].append(
                make_book_entry(i, dtiso, authref, seqref)
            )
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)

    return ret
