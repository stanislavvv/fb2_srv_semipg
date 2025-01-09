# fb2_srv semi-postgres based

## About
fb2_srv_pseudostatic & fb2_srv_pg mix:

  * from fb2_srv_pseudostatic -- json indexes in multiple files
  * from fb2_srv_pg -- use database for search and pictures

## Usage

1. prepare virtual environment by `make venv`
2. copy `app/config.py.example` to `app/config.py` and edit for path in `ZIPS` and `STATIC` and postgres credentials in `PG_*`
3. run following commands for `.zip` processing:

```shell
./datachew.sh new_lists  # prepare .zip.list with books data
./datachew.sh fillonly   # fill database with new books
./datachew.sh stage1     # prepare static data directory
./datachew.sh stage2     # create authors pages data directories/files struct
./datachew.sh stage3     # create sequences pages data
./datachew.sh stage4     # create genres pages data
```

4. run test interface via `./opds.sh` and view it on http://localhost:8000/

or 

4. run production interface via `./gunicorn.sh` and view it on http://localhost:8000/books/

Default interface will be redirected to `html/` for browser. If you need OPDS -- use `opds/` in reader configuration (like http://localhost:8000/books/opds/ )

If you need some public access -- run production on server with nginx and add following piece to site config:

```
    location /books/ {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      
      proxy_read_timeout 600s;
      proxy_send_timeout 600s;
      proxy_connect_timeout 600s;
      proxy_pass http://127.0.0.1:8000/books/;
    }
```
