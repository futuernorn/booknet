booknet
=======
# Getting Started
Aside from the software listed on the course website / included in the provided vagrant configuration, the following python library is needed:

(https://github.com/maxcountryman/flask-login)
```
pip install flask-login
from flask.ext.login import LoginManager
```

# Initalizing Database
1. Execute data/booknet_ddl.sql on the database to drop / reinitalize all tables.
2. Import parsed sample data using data/booknet_11291400_parsed.sql.gz 
```
gunzip < booknet_11291400_parsed.sql.gz  | psql booknet -U postgres
```
~~Use python to execute load-template.py. This will parse and import all sample_data (**provided books.json, authors.json, & works.json should be in data/sample-data**). *TODO: When load-template.py is finalize, replace this step with a (chunkified?) SQL file for import.*~~

3. Execute data/starting_data.sql on the database to import generic starting manual and randomly generated data.

## Generated Data Information
#### list
500 entries
Targeting user_id 1-30

#### book_list
10,000 entries
Targeting book_id 1-5000
Targeting list_id 1-500

#### user_log
5000 entries
Targeting book_id 1-10000
pages_read: 1-1000


## Sample Data Structure Information
------
From http://www.danneu.com/posts/authordb-datomic-tutorial/

> There isn't much documentation to be found, but basically Open Library has a concept of:
>
> Authors
> Works
> Editions
> A Work is the abstract representation of a book. It at least has a title and a set of authors associated with it.
>
> An Author can belong to many books.
>
> An Edition is a concrete publication of a Work. It can contain things like publication dates and it can represent hardcover books, paperbacks, and ebooks. I didn't even crack open the edition data dump (ran out of hard-drive space) but I believe Editions can even have their own Authors.

#####Covers
[Openlibrary.org information](https://openlibrary.org/dev/docs/api/covers)

So in our DDL we will most likely use the following mapping:
Works -> Book Core

Not all data rows have all keys. Here is a breakdown of the total occurences of a given key. Only the more common keys are shown, a full breakdown is [here](doc/data_keys.md).

####Author Keys Occurrences (>89823)

| Key | # | Mapping |
| ---- | ---- | ---- |
| type | 179646 |
| revision | 179646 |
| last_modified | 179646 |
| key | 179646 |
| name | 179646 |
| personal_name | 129425 |



####Work Keys Occurrences (>97470)

| Key | # | Mapping |
| ---- | ---- | ---- |
| latest_revision | 194940 |
| type | 194940 |
| revision | 194940 |
| last_modified | 194940 |
| key | 194940 |
| created | 194940 |
| title | 194938 |
| authors | 192633 |
| subjects | 111842 |



####Book Keys Occurrences (>110721)

| Key | # | Mapping |
| ---- | ---- | ---- |
| work | 221442 |
| type | 221442 |
| revision | 221442 |
| last_modified | 221442 |
| key | 221442 |
| authors | 221442 |
| title | 221409 |
| publish_date | 214048 |
| publishers | 212474 |
| latest_revision | 200212 |
| languages | 197472 |
| number_of_pages | 165089 |
| publish_places | 157332 |
| publish_country | 154235 |
| subjects | 151283 |
| created | 149379 |
| pagination | 146280 |
| by_statement | 112330 |
| isbn_10 | 111199 |

