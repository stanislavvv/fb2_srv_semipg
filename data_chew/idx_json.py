# -*- coding: utf-8 -*-
"""create db and json idx"""

import json
import logging
import gzip
import glob

from pathlib import Path

from .idx import open_booklist
from .strings import unicode_upper, id2path, id2pathonly, quote_string


MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5

auth_processed = {}


def process_lists(db, zipdir, pagesdir, stage):
    """process .list's for static pages"""
    logging.debug("process_lists: %s, %s, %s", zipdir, pagesdir, stage)
    if stage == "global":
        make_global_indexes(db, zipdir, pagesdir)
    elif stage == "authors":
        auth_cnt = db.get_authors_cnt()
        logging.info("Creating authors indexes (total: %d)..." % auth_cnt)
        # while(len(auth_processed) < auth_cnt):
            # make_auth_data(pagesdir)
            # logging.debug(" - processed authors: %d/%d" % (len(auth_processed), auth_cnt))
        make_auth_subindexes(db, pagesdir)
    elif stage == "sequences":
        pass
        # with open(pagesdir + "/allsequencecnt.json") as f:
            # seq_cnt = json.load(f)
        # logging.info("Creating sequences indexes (total: %d)..." % seq_cnt)
        # while(len(seq_processed) < seq_cnt):
            # make_seq_data(pagesdir)
            # logging.debug(" - processed sequences: %d/%d" % (len(seq_processed), seq_cnt))
        # make_seq_subindexes(pagesdir)
    elif stage == "genres":
        pass
        # with open(pagesdir + "/allgenrecnt.json") as f:
            # gen_cnt = json.load(f)
        # logging.info("Creating genres indexes (total: %s)..." % gen_cnt)
        # while(len(gen_processed) < gen_cnt):
            # make_gen_data(pagesdir)
            # logging.debug(" - processed genres: %d/%d" % (len(gen_processed), gen_cnt))
        # make_gen_subindexes(pagesdir)


def make_global_indexes(db, zipdir, pagesdir):
    Path(pagesdir).mkdir(parents=True, exist_ok=True)


def make_auth_subindexes(db, pagesdir):
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
            name3 = char3[0]
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

