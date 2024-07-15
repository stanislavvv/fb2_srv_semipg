# -*- coding: utf-8 -*-

"""module for prepare and index data for opds library"""

import os
import sys
import zipfile
# import glob
import json
import logging

# pylint can't import local's
# pylint: disable=E0401
from .data import get_replace_list, fb2parse

from .inpx import get_inpx_meta

INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip


def recalc_commit(db):  # pylint: disable=C0103
    """precalc some counts in database"""
    logging.info("recalc stored counts...")
    db.recalc_authors_books()
    db.recalc_seqs_books()
    db.recalc_genres_books()
    db.commit()
    logging.info("end")


def create_booklist(inpx_data, zip_file):  # pylint: disable=C0103
    """(re)create .list from .zip"""

    booklist = zip_file + ".list"
    booklistgz = zip_file + ".list.gz"
    if os.path.exists(booklistgz):
        os.remove(booklistgz)  # fix simultaneous .list and .list.gz
    try:
        with open(booklist, 'w', encoding='utf-8') as blist:

            files = list_zip(zip_file)
            z_file = zipfile.ZipFile(zip_file)  # pylint: disable=R1732
            inpx_meta = get_inpx_meta(inpx_data, zip_file)
            replace_data = get_replace_list(zip_file)

            for filename in files:
                logging.debug("%s/%s            ", zip_file, filename)
                _, book = fb2parse(z_file, filename, replace_data, inpx_meta)
                if book is None:
                    continue
                blist.write(json.dumps(book, ensure_ascii=False))  # jsonl in blist
                blist.write("\n")

    except Exception as ex:  # pylint: disable=W0703
        logging.error("error processing zip_file: %s", ex)
        logging.info("removing %s", booklist)
        os.remove(booklist)
        sys.exit(1)
    except KeyboardInterrupt as ex:  # Ctrl-C
        logging.error("error processing zip_file: %s", ex)
        logging.info("removing %s", booklist)
        os.remove(booklist)
        sys.exit(1)


def update_booklist(inpx_data, zip_file):  # pylint: disable=C0103
    """(re)create .list for new or updated .zip"""

    booklist = zip_file + ".list"
    booklistgz = zip_file + ".list.gz"
    replacelist = zip_file + ".replace"
    if os.path.exists(booklist):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklist)
        replacetime = 0
        if os.path.exists(replacelist):
            replacetime = os.path.getmtime(replacelist)
        if ziptime < listtime and replacetime < listtime:
            return False
    elif os.path.exists(booklistgz):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklistgz)
        replacetime = 0
        if os.path.exists(replacelist):
            replacetime = os.path.getmtime(replacelist)
        if ziptime < listtime and replacetime < listtime:
            return False
        os.remove(booklistgz)  # remove outdated .list.gz, because it is not .list
    create_booklist(inpx_data, zip_file)
    return True


def list_zip(zip_file):
    """return list of files in zip_file"""
    ret = []
    z_file = zipfile.ZipFile(zip_file)  # pylint: disable=R1732
    for filename in z_file.namelist():
        if not os.path.isdir(filename):
            ret.append(filename)
    return ret


def ziplist(inpx_data, zip_file):
    """iterate over files in zip, return array of book struct"""

    logging.info(zip_file)
    ret = []
    z_file = zipfile.ZipFile(zip_file)  # pylint: disable=R1732
    replace_data = get_replace_list(zip_file)
    inpx_data = get_inpx_meta(inpx_data, zip_file)
    for filename in z_file.namelist():
        if not os.path.isdir(filename):
            logging.debug("%s/%s            ", zip_file, filename)
            _, res = fb2parse(z_file, filename, replace_data, inpx_data)
            ret.append(res)
    return ret
