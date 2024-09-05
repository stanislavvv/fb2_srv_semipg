# -*- coding: utf-8 -*-
"""create db and json idx"""

import json
import logging
import glob

from pathlib import Path
from functools import cmp_to_key

from .idx import open_booklist
from .strings import id2path, id2pathonly, quote_string, string2filename
from .data import seqs_in_data, nonseq_from_data, refine_book, custom_alphabet_book_title_cmp

MAX_PASS_LENGTH = 4000
MAX_PASS_LENGTH_GEN = 5

auth_processed = {}
seq_processed = {}
gen_processed = {}

# pylint: disable=C0103,W0613


def process_lists(db, zipdir, pagesdir, stage, hide_deleted=False):
    """process .list's for static pages"""

    if stage == "global":
        make_global_indexes(db, zipdir, pagesdir)
    elif stage == "authors":
        auth_cnt = db.get_data("get_authors_cnt")[0][0]
        logging.info("Creating authors indexes (total: %d)...", auth_cnt)
        while len(auth_processed) < auth_cnt:
            make_auth_data(db, zipdir, pagesdir, hide_deleted)
            logging.debug(" - processed authors: %d/%d", len(auth_processed), auth_cnt)
        make_auth_subindexes(db, pagesdir)
    elif stage == "sequences":
        seq_cnt = db.get_data("get_seqs_cnt")[0][0]
        logging.info("Creating sequences indexes (total: %d)...", seq_cnt)
        while len(seq_processed) < seq_cnt:
            make_seq_data(db, zipdir, pagesdir, hide_deleted)
            logging.debug(" - processed sequences: %d/%d", len(seq_processed), seq_cnt)
        make_seq_subindexes(db, pagesdir)
    elif stage == "genres":
        pass
        gen_cnt = db.get_data("get_genres_cnt")[0][0]
        logging.info("Creating genres indexes (total: %s)..." % gen_cnt)
        while (len(gen_processed) < gen_cnt):
            make_gen_data(db, zipdir, pagesdir, hide_deleted)
            logging.debug(" - processed genres: %d/%d" % (len(gen_processed), gen_cnt))
        make_gen_subindexes(db, pagesdir)
    else:
        logging.error("Unknow stage")


def make_global_indexes(db, zipdir, pagesdir):
    """make root dir for static data"""
    Path(pagesdir).mkdir(parents=True, exist_ok=True)


def make_auth_subindexes(db, pagesdir):  # pylint: disable=R0914
    """make character indexes for authors"""
    authidxbase = "/authorsindex/"
    workdir = pagesdir + authidxbase
    Path(workdir).mkdir(parents=True, exist_ok=True)

    alpha = []
    auth_root = {}
    idx1 = db.get_data("get_authors_one")
    for char1 in idx1:
        char = char1[0]
        alpha.append(char)
        auth_root[char] = 1
        Path(workdir + char).mkdir(parents=True, exist_ok=True)
        idx3 = db.get_data_par1("get_authors_three", quote_string(char))
        auth_three = {}
        for char3 in idx3:
            name3 = string2filename(char3[0])
            cnt3 = char3[1]
            auth_three[name3] = cnt3
            auth_list = {}
            for auth in db.get_data_par1("get_authors", quote_string(name3)):
                auth_id = auth[0]
                auth_name = auth[1]
                auth_list[auth_id] = auth_name
            with open(workdir + char + "/%s.json" % name3, "w") as f:
                json.dump(auth_list, f, indent=2, ensure_ascii=False)
        # make three letters index for first letter
        with open(workdir + char + "/index.json", "w") as f:
            json.dump(auth_three, f, indent=2, ensure_ascii=False)
    # make first letters index
    with open(workdir + "index.json", "w") as f:
        json.dump(auth_root, f, indent=2, ensure_ascii=False)


def make_auth_data(db, zipdir, pagesdir, hide_deleted=False):  # pylint: disable=R0914
    """make per-author data"""
    auth_data = {}
    for booklist in sorted(glob.glob(zipdir + '/*.zip.list') + glob.glob(zipdir + '/*.zip.list.gz')):
        with open_booklist(booklist) as lst:
            for b in lst:
                book = json.loads(b)
                if book is None:
                    continue
                if hide_deleted and "deleted" in book and book["deleted"] != 0:
                    continue
                book = refine_book(db, book)
                if book["authors"] is not None:
                    book = refine_book(db, book)
                    for auth in book["authors"]:
                        auth_id = auth.get("id")
                        auth_name = auth.get("name")
                        if auth_id not in auth_processed:
                            if auth_id in auth_data:
                                s = auth_data[auth_id]["books"]
                                s.append(book)
                                auth_data[auth_id]["books"] = s
                            elif len(auth_data) < MAX_PASS_LENGTH:
                                s = {"name": auth_name, "id": auth_id}
                                b = []
                                b.append(book)
                                s["books"] = b
                                auth_data[auth_id] = s
    for auth_id in auth_data:
        data = auth_data[auth_id]

        workdir = pagesdir + "/author/" + id2path(auth_id)
        Path(workdir).mkdir(parents=True, exist_ok=True)

        allbooks = data["books"]
        workfile = workdir + "/all.json"
        with open(workfile, 'w') as idx:
            json.dump(allbooks, idx, indent=2, ensure_ascii=False)

        seqs = seqs_in_data(auth_data[auth_id]["books"])
        workfile = workdir + "/sequences.json"
        with open(workfile, 'w') as idx:
            json.dump(seqs, idx, indent=2, ensure_ascii=False)

        nonseqs = nonseq_from_data(auth_data[auth_id]["books"])
        workfile = workdir + "/sequenceless.json"
        with open(workfile, 'w') as idx:
            json.dump(nonseqs, idx, indent=2, ensure_ascii=False)

        main = data
        del main["books"]
        workfile = workdir + "/index.json"
        with open(workfile, 'w') as idx:
            json.dump(main, idx, indent=2, ensure_ascii=False)
        auth_processed[auth_id] = 1


def make_seq_subindexes(db, pagesdir):  # pylint: disable=R0914
    """make char indexes for seqs"""
    seqidxbase = "/sequencesindex/"
    workdir = pagesdir + seqidxbase
    Path(workdir).mkdir(parents=True, exist_ok=True)

    alpha = []
    seq_root = {}
    idx1 = db.get_data("get_seqs_one")
    for char1 in idx1:
        char = char1[0]
        alpha.append(char)
        seq_root[char] = 1
        Path(workdir + char).mkdir(parents=True, exist_ok=True)
        idx3 = db.get_data_par1("get_seqs_three", quote_string(char))
        seq_three = {}
        for char3 in idx3:
            name3 = string2filename(char3[0])
            cnt3 = char3[1]
            seq_three[name3] = cnt3
            seq_list = {}
            for seq in db.get_data_par1("get_seqs", quote_string(name3)):
                seq_id = seq[0]
                seq_name = seq[1]
                seq_list[seq_id] = seq_name
            with open(workdir + char + "/%s.json" % name3, "w") as f:
                json.dump(seq_list, f, indent=2, ensure_ascii=False)
        # make three letters index for first letter
        with open(workdir + char + "/index.json", "w") as f:
            json.dump(seq_three, f, indent=2, ensure_ascii=False)
    # make first letters index
    with open(workdir + "index.json", "w") as f:
        json.dump(seq_root, f, indent=2, ensure_ascii=False)


def make_seq_data(db, zipdir, pagesdir, hide_deleted=False):  # pylint: disable=R0914
    """make per-sequence data"""
    seq_data = {}
    for booklist in sorted(glob.glob(zipdir + '/*.zip.list') + glob.glob(zipdir + '/*.zip.list.gz')):
        with open_booklist(booklist) as lst:
            for b in lst:
                book = json.loads(b)
                if book is None:
                    continue
                if hide_deleted and "deleted" in book and book["deleted"] != 0:
                    continue
                book = refine_book(db, book)
                if book["sequences"] is not None:
                    for seq in book["sequences"]:
                        seq_id = seq.get("id")
                        seq_name = seq.get("name")
                        if seq_id is not None and seq_id not in seq_processed:
                            if seq_id in seq_data:
                                s = seq_data[seq_id]["books"]
                                s.append(book)
                                seq_data[seq_id]["books"] = s
                            elif len(seq_data) < MAX_PASS_LENGTH:
                                s = {"name": seq_name, "id": seq_id}
                                b = []
                                b.append(book)
                                s["books"] = b
                                seq_data[seq_id] = s
    for seq_id in seq_data:
        data = seq_data[seq_id]
        workdir = pagesdir + "/sequence/" + id2pathonly(seq_id)
        workfile = pagesdir + "/sequence/" + id2path(seq_id) + ".json"
        Path(workdir).mkdir(parents=True, exist_ok=True)
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        seq_processed[seq_id] = 1


def make_gen_subindexes(db, pagesdir):  # pylint: disable=R0914
    genidxbase = "/genresindex/"
    workdir = pagesdir + genidxbase
    Path(workdir).mkdir(parents=True, exist_ok=True)
    metas = db.get_data("get_metas")

    data = {}
    for meta in metas:
        meta_id = meta[0]
        meta_name = meta[1]
        data[meta_id] = meta_name
    workfile = workdir + "index.json"
    with open(workfile, 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)

    for meta_id in data:
        workfile = workdir + str(meta_id) + ".json"
        gdata = db.get_data_par1("get_genres_in_meta", meta_id)
        genre_data = {}
        for gen in gdata:
            gen_id = gen[0]
            gen_name = gen[1]
            genre_data[gen_id] = gen_name
        with open(workfile, 'w') as idx:
            json.dump(genre_data, idx, indent=2, ensure_ascii=False)


def make_gen_data(db, zipdir, pagesdir, hide_deleted=False):  # pylint: disable=R0912,R0914
    """make per-genres book lists"""
    # global gen_idx
    # global gen_processed
    genres = db.genres

    gen_data_base = "/genre/"  # for genre data
    gen_data = {}
    gen_names = {}

    for booklist in sorted(glob.glob(zipdir + '/*.zip.list') + glob.glob(zipdir + '/*.zip.list.gz')):
        with open_booklist(booklist) as lst:
            for b in lst:
                book = json.loads(b)
                if book is None:
                    continue
                if hide_deleted and "deleted" in book and book["deleted"] != 0:
                    continue
                book = refine_book(db, book)
                if book["genres"] is not None:
                    for gen in book["genres"]:
                        gen_id = gen
                        gen_name = gen
                        if gen in genres:
                            gen_name = genres[gen]["descr"]
                        gen_names[gen_id] = gen_name
                        if gen_id not in gen_processed:
                            if gen_id in gen_data:
                                s = gen_data[gen_id]
                                s.append(book)
                                gen_data[gen_id] = s
                            elif len(gen_data) < MAX_PASS_LENGTH_GEN:
                                s = []
                                s.append(book)
                                gen_data[gen_id] = s
    workdir = pagesdir + gen_data_base
    Path(workdir).mkdir(parents=True, exist_ok=True)
    for gen in gen_data:
        workdir = pagesdir + gen_data_base + gen
        Path(workdir).mkdir(parents=True, exist_ok=True)

        # data = {"id": gen, "name": gen_names[gen], "books": gen_data[gen]}
        data = []
        for book in gen_data[gen]:
            data.append(book["book_id"])

        workfile = pagesdir + gen_data_base + gen + "/all.json"
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)

        i = 0
        data = sorted(gen_data[gen], key=cmp_to_key(custom_alphabet_book_title_cmp))
        while len(data) > 0:
            wdata = data[:50]
            data = data[50:]
            workfile = pagesdir + gen_data_base + gen + "/" + str(i) + ".json"
            with open(workfile, 'w') as idx:
                json.dump(wdata, idx, indent=2, ensure_ascii=False)
            i = i + 1
        gen_processed[gen] = 1
