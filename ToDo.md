# To Do

1. datachew subcommands:
  * `clean` (or may be not?)
  * `lists`, `new_lists` -- exactly as in fb2_srv_pg
  * `fillonly`, `fillall` -- partially as in fb2_srv_pg: data in postgress will be used for search and random pages
  * `stage*` -- partially as in fb2_srv_pseudostatic: all other pages
2. web application -- mix of fb2_srv_pg and fb2_srv_pseudostatic

# планируемый список страниц webapp (со стороны opds):

tags for pages:
  * [db] -- must use database
  * [file] -- use prepared files
  * [zip] -- work with zip (mostly read fb2)
  * [int] -- only internal app data used
  * [?] -- unknown

## common:
DONE

  * `/` -- app root page, redirect to `/html/` (or make page with some info?) [int]
  * `/opds/` -- library root, opds interface (`s/opds/html/` for web interface) [int]

## static and books access:
DONE

  * `/fb2/<zip_file>/<filename>` -- book as is (fb2) [zip]
  * `/read/<zip_file>/<filename>` -- book in html [zip]
  * `/st/<filename>` -- static app files [int]
  * `/conver/<book_id>/jpg` -- book cover image [db][file]

## authors:
DONE

  * `/opds/authorsindex/` -- alphabet of authors names first letters [file]
  * `/opds/authorsindex/<sub>` -- three letters list (one-letter sub) and authors list (three-letter sub) [file]
  * `/opds/author/<sub1>/<sub2>/<id>` -- author's page [file]
  * `/opds/author/<sub1>/<sub2>/<id>/sequences` -- author's sequences list [file]
  * `/opds/author/<sub1>/<sub2>/<id>/<seq_id>` -- books in author's sequence [file][db]
  * `/opds/author/<sub1>/<sub2>/<id>/sequenceless` -- books of author not belonged to any sequence [file][db]
  * `/opds/author/<sub1>/<sub2>/<id>/alphabet` -- all books of author sort by alphabet [file][db]
  * `/opds/author/<sub1>/<sub2>/<id>/time` -- all books of author sort by time [file][db]

## sequences:
DONE

  * `/opds/sequencesindex/` -- alphabet of sequences names first letters [file]
  * `/opds/sequencesindex/<sub>` -- three letters list (one-letter sub) and sequences list (three-letter sub) [file]
  * `/opds/sequence/<sub1>/<sub2>/<id>` -- books in sequence [file]

## genres:
DONE

  * `/opds/genresindex/` -- genres meta list [file]
  * `/opds/genresindex/<sub>` -- genres list in meta "sub" [file]
  * `/opds/genre/<id>`, `/opds/genre/<id>/<page>` -- books in genres [file]|[db]?

## books by time:
  * `/opds/time`, `/opds/time/<page>` -- books by time, desc [file]?

## search:
  * `/opds/search` -- main search (links to other search pages) [int]
  * `/opds/search-books` -- books list with search term in title [db]
  * `/opds/search-booksanno` -- books list with search term in annotation [db]
  * `/opds/search-authors` -- list of authors with search term in name [db]
  * `/opds/search-sequences` -- list of sequenses with search term in name [db]

## random:
  * `/opds/random-books/` -- random books list (new at reload) [db]|[file]?
  * `/opds/random-sequences/` -- random sequences list (new at reload) [db]|[file]?
  * `/opds/rnd-genresindex/` -- genres meta list (static) [file]
  * `/opds/rnd-genresindex/<sub>` -- genres list in meta (static) [file]
  * `/opds/rnd-genre/<id>` -- random books in genre (new at reload) [db]|[file]?

## Вероятные данные в БД:
1. book_id, title -- тут, возможно добавятся данные, необходимые для отображения списка книг, может быть в отдельной таблице
2. book_id, annotation
3. author_id, author_name
4. sequence_id, sequence_name

## Вероятная структура каталогов на диске:

переменные в описании структуры:
  * sub1 и sub2 -- соответственно, первые два и вторые два символа от id
  * letter -- первая буква имени (напр. автора)
  * threeletter -- первые три буквы имени
  * metaid -- id метажанра (группы жанров)
  * id -- идентификатор книги/автора/серии/жанра
  * page -- номер страницы, с 0

1. По авторам:
  * `authorsindex/`
    * `authorsindex/index.json` -- алфавитный список первых букв имён авторов
    * `authorsindex/<letter>/` -- каталог индексов для первой буквы имени
      * `authorsindex/<letter>/index.json` -- список первых трёх букв имён авторов на конкретную первую букву
      * `authorsindes/<letter>/<threeletter>.json` -- список id + имя авторов (так, как требуется для отображения на странице)
  * `author/<sub1>/<sub2>/<id>/` -- основной каталог для данных о конкретном авторе
    * `author/<sub1>/<sub2>/<id>/index.json` -- общая информация об авторе
    * `author/<sub1>/<sub2>/<id>/sequences.json` -- список серий автора с id книг в серии
    * `author/<sub1>/<sub2>/<id>/sequenceless.json` -- список id книг автора вне серий
    * `author/<sub1>/<sub2>/<id>/all.json` -- список id всех книг автора (сортировка для страниц ../alphabet и ../time - в приложении)
2. По сериям:
  * `sequencesindex/`
    * `sequencesindex/index.json` -- алфавитный список первых букв названий серий
    * `sequencesindex/<letter>/` -- каталог индексов для первой буквы
      * `sequencesindex/<letter>/index.json` -- список первых трёх букв из названий серий на конкретную букву
      * `sequencesindex/<letter>/<threeletter>.json` -- список id + название серии
  * `sequence/<sub1>/<sub2>/<id>/` -- основной каталог для данных о конкретной серии
    * `sequence/<sub1>/<sub2>/<id>/index.json` -- название серии + список id книг в серии
3. По жанрам:
  * `genresindex/`
    * `genresindex/index.json` -- алфавитный список метажанров с их metaid
    * `genresindex/<meta>.json` -- алфавитный список жанров с их id, принадлежащих metaid
  * `genre/` -- данный каталог понадобится только если списки книг не будут браться из БД
    * `genre/<id>/` -- каталог для конкретного жанра
    * `genre/<id>/all.json` -- все id книг
    * `genre/<id>/index.json` -- id книг для первой страницы жанра (то же содержимое -- для `0.json`)
    * `genre/<id>/<page>.json` -- id книг для страницы с номером page
