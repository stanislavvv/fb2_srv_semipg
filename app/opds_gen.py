# -*- coding: utf-8 -*-
"""library opds functions for authors pages"""

import json

from functools import cmp_to_key
from flask import current_app

from .consts import URL
from .internals import get_dtiso, custom_alphabet_book_title_cmp, get_randoms, get_books_descr
from .opds import ret_hdr, add_link, make_book_entry
from .db import dbconnect

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


def rnd_genre_books(params):  # pylint: disable=R0914
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

    workdir = rootdir + URL["genre"].replace("/opds", "") + gen_id + "/"
    workfile = workdir + "all.json"

    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret = add_link(ret, approot + self, "self", "application/atom+xml;profile=opds-catalog")
    ret = add_link(ret, approot + upref, "up", "application/atom+xml;profile=opds-catalog")

    books = []
    try:
        with open(workfile) as nm:
            book_ids = json.load(nm)

        maxnum = len(book_ids)
        limit = int(current_app.config['PAGE_SIZE'])

        nums = get_randoms(limit, maxnum - 1)
        rnd_book_ids = []
        for n in nums:
            rnd_book_ids.append(book_ids[n])

        db_conn = dbconnect()
        dbdata = db_conn.get_books_byids(rnd_book_ids)
        book_descr = get_books_descr(rnd_book_ids)

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

        books = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))
        for book in books:
            ret["feed"]["entry"].append(make_book_entry(book, dtiso, authref, seqref))
    except Exception as e:  # pylint: disable=W0703
        print(e)

    return ret
