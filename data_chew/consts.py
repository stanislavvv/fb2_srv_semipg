# -*- coding: utf-8 -*-

"""some string constats for indexing and db"""

CREATE_REQ = [
    # trigram fast search
    """
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    """,
    """
    CREATE TABLE IF NOT EXISTS books (
        zipfile	varchar NOT NULL,
        filename	varchar NOT NULL,
        genres	varchar ARRAY,
        book_id	char(32) UNIQUE,
        lang	    varchar,
        date	    date,
        size	    integer,
        deleted   boolean,
        PRIMARY KEY(book_id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS books_zipfile ON books (zipfile);
    """,
    """
    CREATE INDEX IF NOT EXISTS books_genres ON books USING GIN ((genres));
    """,
    """
    CREATE TABLE IF NOT EXISTS books_descr (
        book_id      char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        book_title   text,
        pub_isbn     varchar,
        pub_year     varchar,
        publisher    text,
        publisher_id char(32),
        annotation   text
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_title ON books_descr USING GIN (book_title gin_trgm_ops);
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_anno ON books_descr USING GIN (annotation gin_trgm_ops);
    """,
    """
    CREATE TABLE IF NOT EXISTS books_covers (
        book_id     char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        cover_ctype varchar,
        cover       text
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_anno_book_id ON books_covers (book_id);
    """,
    """
    CREATE TABLE IF NOT EXISTS authors (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS authors_names ON authors USING GIN (name gin_trgm_ops);
    """,
    """
    CREATE TABLE IF NOT EXISTS sequences (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS seq_names ON sequences USING GIN (name gin_trgm_ops);
    """,
    """
    CREATE TABLE IF NOT EXISTS genres_meta (
        meta_id     integer NOT NULL,
        name        text NOT NULL,
        description     text DEFAULT '',
        PRIMARY KEY(meta_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS genres (
        id              varchar UNIQUE NOT NULL,
        meta_id     integer REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        name        TEXT NOT NULL,
        cnt         integer DEFAULT 0,
        description     text DEFAULT '',
        PRIMARY KEY(id)
    );
    """
]

INSERT_REQ = {
    "books": """
        INSERT INTO books(zipfile, filename, genres, book_id, lang, date, size, deleted)
        VALUES ('%s', '%s', %s, '%s', '%s', '%s', %s, CAST (%s AS boolean));
    """,
    "book_replace": """
        UPDATE books SET zipfile = '%s', filename = '%s', genres = %s,
        lang = '%s', date = '%s', size = %d, deleted = CAST (%s AS boolean)
        WHERE book_id = '%s';
    """,
    "bookdescr": """
        INSERT INTO books_descr(book_id, book_title, pub_isbn,
        pub_year, publisher, publisher_id, annotation)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """,
    "bookdescr_replace": """
        UPDATE books_descr SET book_title = %s, pub_isbn = %s, pub_year = %s, publisher = %s,
        publisher_id = %s, annotation = %s
        WHERE book_id = %s;
    """,
    "cover": """
        INSERT INTO books_covers(book_id, cover_ctype, cover)
        VALUES ('%s', '%s', '%s');
    """,
    "cover_replace": """
        UPDATE books_covers SET cover_ctype = '%s', cover = '%s' WHERE book_id = '%s';
    """,
    "author": """
        INSERT INTO authors(id, name) VALUES ('%s', '%s');
    """,
    "sequences": """
        INSERT INTO sequences(id, name) VALUES ('%s', '%s');
    """,
    "genres": """
        INSERT INTO genres(id, meta_id, name, cnt, description) VALUES ('%s', '%s', '%s', %s, '%s');
    """,
    "meta": """
        INSERT INTO genres_meta(meta_id, name, description) VALUES (%s, '%s', '%s');
    """,
    "genre_cnt_update": """
        UPDATE genres SET cnt = %s WHERE id = '%s';
    """
}

GET_REQ = {
    "genre_exist": """
        SELECT 1 FROM genres WHERE id = '%s';
    """,
    "meta_exist": """
        SELECT 1 FROM genres_meta WHERE meta_id = '%s';
    """,
    "get_genre_cnt": """
        SELECT cnt FROM genres WHERE id = '%s';
    """,
    "get_seqs_ids": """
        SELECT id FROM sequences;
    """,
    "get_genres_ids": """
        SELECT id FROM genres;
    """,
    "get_genre_books_cnt": """
        SELECT count(book_id) as cnt FROM books WHERE '%s' = ANY (genres);
    """,
    "get_authors_ids": """
        SELECT id FROM authors;
    """,
    "get_authors_ids_by_ids": """
        SELECT id FROM authors WHERE id in ('%s');
    """,
    "get_authors_cnt": """
        SELECT count(*) FROM authors;
    """,
    "get_authors_one": """
        SELECT upper(substring(name, 1, 1)) as name1 FROM authors GROUP BY name1;
    """,
    "get_authors_three": """
        SELECT upper(substring(name, 1, 3)) as name3, count(*) as cnt
        FROM authors
        WHERE upper(substring(name, 1, 1)) = '%s' GROUP BY name3;
    """,
    "get_authors": """
        SELECT id, name FROM authors WHERE upper(substring(name, 1, 3)) = '%s';
    """,
    "get_seqs_cnt": """
        SELECT count(*) FROM sequences;
    """,
    "get_seqs_one": """
        SELECT upper(substring(name, 1, 1)) as name1 FROM sequences GROUP BY name1;
    """,
    "get_seqs_three": """
        SELECT upper(substring(name, 1, 3)) as name3, count(*) as cnt
        FROM sequences
        WHERE upper(substring(name, 1, 1)) = '%s' GROUP BY name3;    """,
    "get_seqs": """
        SELECT id, name FROM sequences
        WHERE upper(substring(sequences.name, 1, 3)) = '%s' GROUP BY id, name;
    """
}
