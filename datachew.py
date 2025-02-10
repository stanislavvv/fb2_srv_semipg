#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main indexing script"""

import sys
import glob
import logging

from app import create_app

from data_chew import INPX
from data_chew import create_booklist, update_booklist, process_lists_db
from data_chew.data import set_data_config
from data_chew.db import BookDB
from data_chew.idx_json import process_lists

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


def usage():
    """print help"""
    print("Usage: datachew.py <command>")
    print("Commands:")
    # print(" clean     -- remove static data from disk")
    print(" lists     -- make all lists from zips, does not touch database")
    print(" new_lists -- update lists from updated/new zips, does not touch database")
    print(" tables    -- prepare tables in database")
    print(" fillonly  -- quickly fill all existing lists to database, but only books not in db")
    print(" fillall   -- quickly fill all existing lists to database, update existing")
    print(" stage[1-4]  -- stage1, ..., stage4 for creating static pages")
    print("full data processing: `for i in new_lists tables fillonly stage1 stage2 stage3 stage4; do ./datachew.py $i; done`")


def clean():
    """clean index data"""


def renew_lists():
    """recreate all .list's from .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
        i += 1
        logging.info("[%s] %s", (str(i)), zip_file)
        create_booklist(inpx_data, zip_file)
    logging.info("[end]")


def new_lists():
    """create .list's for new or updated .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
        i += 1
        logging.info("[%s] %s", (str(i)), zip_file)
        update_booklist(inpx_data, zip_file)
    logging.info("[end]")


def fromlists(stage):
    """index .lists to database"""
    zipdir = app.config['ZIPS']
    pg_host = app.config['PG_HOST']
    pg_base = app.config['PG_BASE']
    pg_user = app.config['PG_USER']
    pg_pass = app.config['PG_PASS']
    hide_deleted = app.config['HIDE_DELETED']
    db = BookDB(pg_host, pg_base, pg_user, pg_pass)  # pylint: disable=C0103
    if stage in ("global", "authors", "sequences", "genres"):
        zipdir = app.config['ZIPS']
        pagesdir = app.config['STATIC']
        process_lists(db, zipdir, pagesdir, stage, hide_deleted=hide_deleted)
    else:
        try:
            process_lists_db(db, zipdir, str(stage), hide_deleted=hide_deleted)
        except Exception as ex:  # pylint: disable=broad-except
            logging.error(ex)
            logging.error("data rollbacked")
    db.conn.close()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        app = create_app()
        DEBUG = app.config['DEBUG']
        DBLOGLEVEL = app.config['DBLOGLEVEL']
        DBLOGFORMAT = app.config['DBLOGFORMAT']
        logging.basicConfig(level=DBLOGLEVEL, format=DBLOGFORMAT)
        if "PIC_WIDTH" in app.config:
            set_data_config("width", app.config['PIC_WIDTH'])
        if sys.argv[1] == "clean":
            clean()
        # elif sys.argv[1] == "asnew":
            # fillall()
        elif sys.argv[1] == "lists":
            renew_lists()
        elif sys.argv[1] == "new_lists":
            new_lists()
        elif sys.argv[1] == "tables":
            fromlists("maketables")
        elif sys.argv[1] == "fillall":
            fromlists("fillall")
        elif sys.argv[1] == "fillonly":
            fromlists("fillonly")
        elif sys.argv[1] == "stage1":
            fromlists("global")
        elif sys.argv[1] == "stage2":
            fromlists("authors")
        elif sys.argv[1] == "stage3":
            fromlists("sequences")
        elif sys.argv[1] == "stage4":
            fromlists("genres")
        else:
            usage()
    else:
        usage()
