# -*- coding: utf-8 -*-
"""create db and json idx"""

import json
import logging
import gzip

# pylint: disable=E0402,C0209
from .consts import INSERT_REQ, GET_REQ
from .strings import quote_string
from .db import sarray2pg, bdatetime2date, make_book_descr

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5

PASS_SIZE_HINT = 10485760


def open_booklist(booklist):
    """return file object of booklist in plain or compressed format"""
    if booklist.find('gz') >= len(booklist) - 3:  # pylint: disable=R1705
        return gzip.open(booklist)
    else:
        return open(booklist, encoding="utf-8")


def process_list_books_batch_db(db, booklist, stage, hide_deleted=False):  # pylint: disable=C0103,R0912,R0914
    """index .list to database"""
    with open_booklist(booklist) as lst:
        count = 0
        lines = lst.readlines(PASS_SIZE_HINT)
        while len(lines) > 0:
            count = count + len(lines)
            # print("   %s" % count)
            logging.info("   %s", count)
            process_books_batch(db, lines, stage, hide_deleted)
            db.commit()
            lines = lst.readlines(PASS_SIZE_HINT)


def process_books_batch(db, booklines, stage, hide_deleted=False):  # pylint: disable=C0103,R0912,R0914,R0915
    """index .list to database"""

    books = []
    authors = {}
    seqs = []
    genres = {}
    book_ids = []
    book_ids_exists = {}
    book_insert = []
    book_update = []
    deleted_cnt = 0

    for line in booklines:
        book = json.loads(line)
        if book is None:
            continue
        if "genres" not in book or book["genres"] in (None, "", []):
            # book["genres"] is None or book["genres"] == "" or book["genres"] == []:
            book["genres"] = ["other"]
        book["genres"] = db.genres_replace(book, book["genres"])
        book["lang"] = db.lang_replace(book, book["lang"])
        if "deleted" not in book:
            book["deleted"] = 0
        if hide_deleted and book["deleted"] != 0:
            deleted_cnt = deleted_cnt + 1
            continue
        books.append(book)
        book_ids.append(book["book_id"])
        if book["sequences"] is not None:
            for seq in book["sequences"]:
                seqs.append(seq)
        for gen in book["genres"]:
            genres[gen] = 1
        for author in book["authors"]:
            auth_id = author["id"]
            authors[auth_id] = author
    # print("     skip deleted books: %d" % deleted_cnt)
    if deleted_cnt > 0:
        logging.debug("     skip deleted books: %d", deleted_cnt)
    db.cur.execute("SELECT book_id FROM books WHERE book_id IN ('%s');" % "','".join(book_ids))
    ret = db.cur.fetchall()
    for row in ret:
        book_ids_exists[row[0]] = 1

    for book in books:
        if book["book_id"] in book_ids_exists:
            book_update.append(book)
        else:
            book_insert.append(book)

    if len(seqs) > 0:
        # logging.debug("sequences...")
        # print("sequences: %d" % len(seqs))
        req = make_insert_seqs(db, seqs)
        if req != "" and len(req) > 10:
            db.cur.execute(req)

    if len(genres.keys()) > 0:
        # logging.debug("genres...")
        # print("genres: %d" % len(genres))
        insert_genres(db, genres.keys())

    if len(authors) > 0:
        # logging.debug("authors...")
        # print("authors: %d" % len(authors))
        req = make_insert_authors(db, authors)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)

    if len(book_insert) > 0:
        # logging.debug("books...")
        # print("books: %d" % len(books))
        req = make_inserts(db, book_insert)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)

    if len(book_update) > 0 and stage == "fillall":
        # print("books for update: %d..." % len(book_update))
        logging.debug("books for update: %d...", len(book_update))
        req = make_updates(db, book_update)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)
        # logging.debug("end slice")

    return True


def make_insert_seqs(db, seqs):  # pylint: disable=C0103
    """create inserts if seqs not in db"""
    inserts = []
    seq_ids = []
    seq_ids_exist = {}
    seqs_ins = []
    seq_done = {}
    for seq in seqs:
        if seq is not None and "id" in seq:
            seq_ids.append(seq["id"])
    req = "SELECT id FROM sequences WHERE id in ('%s');" % "','".join(seq_ids)
    db.cur.execute(req)
    ids = db.cur.fetchall()
    if ids is not None:
        for seq in ids:
            seq_ids_exist[seq[0]] = 1
    for seq in seqs:
        if "id" in seq and seq["id"] not in seq_ids_exist:
            seqs_ins.append(seq)
    for seq in seqs_ins:
        if "id" in seq:
            if seq["id"] in seq_done:
                pass  # debug was here
            else:
                inserts.append(INSERT_REQ["sequences"] % (seq["id"], quote_string(seq["name"])))
                seq_done[seq["id"]] = 1
    return "".join(inserts)


def insert_genres(db, genres):  # pylint: disable=C0103
    """insert genres to db"""
    for gen in genres:
        db.add_genre(gen)


def make_insert_authors(db, authors):  # pylint: disable=C0103
    """make insert for new authors"""
    auth_exist = {}
    inserts = []
    req = GET_REQ["get_authors_ids_by_ids"] % "','".join(authors.keys())
    db.cur.execute(req)
    ids = db.cur.fetchall()

    if ids is not None:
        for item in ids:
            auth_exist[item[0]] = 1

    for auth in authors.keys():
        # logging.debug(">> %s: %s", auth, authors[auth])
        if auth in auth_exist:
            pass  # debug was here
        else:
            author = authors[auth]
            req = INSERT_REQ["author"] % (author["id"], quote_string(author["name"]))
            inserts.append(req)
    return "".join(inserts)


def make_inserts(db, books):  # pylint: disable=C0103
    """create inserts for every book"""
    inserts = []
    for book in books:
        ins = make_insert_book(db, book)
        inserts.append(ins)
    return "".join(inserts)


def make_updates(db, books):  # pylint: disable=C0103
    """create inserts for every book"""
    inserts = []
    for book in books:
        ins = make_update_book(db, book)
        inserts.append(ins)
    return "".join(inserts)


def get_ids(data):
    """return id fields array"""
    ret = []
    if data is not None:
        for i in data:
            if "id" in i:
                ret.append(i["id"])
    return ret


def make_insert_book(db, book):  # pylint: disable=C0103,R0912,R0914,R0915,R1702
    """return inserts for book"""
    req = []
    global authors_seqs  # pylint: disable=W0602,W0603,C0103
    gnrs = sarray2pg(book["genres"])
    authors = sarray2pg(get_ids(book["authors"]))
    seqs = sarray2pg(get_ids(book["sequences"]))
    bdate = bdatetime2date(book["date_time"])
    book_ins = (
        book["zipfile"],
        book["filename"],
        gnrs,
        authors,
        seqs,
        book["book_id"],
        book["lang"],
        bdate,
        int(book["size"]),
        book["deleted"]
    )
    req.append(INSERT_REQ["books"] % book_ins)

    bookdescr = make_book_descr(book)
    req.append(INSERT_REQ["bookdescr"] % bookdescr)
    book_id = book["book_id"]

    if "cover" in book and book["cover"] is not None:
        cover = book["cover"]
        cover_ctype = cover["content-type"]
        cover_data = cover["data"]
        req.append(INSERT_REQ["cover"] % (book_id, cover_ctype, cover_data))
    return "".join(req)


def make_update_book(db, book):  # pylint: disable=C0103,R0912,R0914,R0915,R1702
    """return updates/inserts/delete for book"""
    req = []
    global authors_seqs  # pylint: disable=W0602,W0603,C0103
    gnrs = sarray2pg(book["genres"])
    bdate = bdatetime2date(book["date_time"])
    book_ins = (
        book["zipfile"],
        book["filename"],
        gnrs,
        book["lang"],
        bdate,
        int(book["size"]),
        book["deleted"],
        book["book_id"]
    )
    req.append(INSERT_REQ["book_replace"] % book_ins)

    bookdescr = make_book_descr(book, update=True)
    req.append(INSERT_REQ["bookdescr_replace"] % bookdescr)
    book_id = book["book_id"]

    if "cover" in book and book["cover"] is not None:
        cover = book["cover"]
        cover_ctype = cover["content-type"]
        cover_data = cover["data"]
        req.append(INSERT_REQ["cover_replace"] % (cover_ctype, cover_data, book_id))

    return "".join(req)
