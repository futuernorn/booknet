booknet
=======
# Getting Started
Aside from the software listed on the course website / included in the provided vagrant configuration, the following python library is needed:

(https://github.com/maxcountryman/flask-login)
```
pip install flask-login
from flask.ext.login import LoginManager
```

I've copied the compiled version (compiled on the class vagrant configuration) of this module to the root directory of the project as well.

# Initalizing Database
* Import latest database data with the following command run from the root directory of the project:
```
gunzip < data/data-dump.sql.gz  | psql booknet -U postgres
```

* Now you can run BookServer.py to start the project / flask.

* As an aside, the book covers that were able to be downloaded and used for our project are located [here](http://goo.gl/7twwVq). However it should happily fail with blank images without that ~350MB download.

# Final Report
* [Data model diagram](doc/data_model_diagram.pdf)
* [List of pages](doc/page_list.pdf)

---------------

## Generated Data Information
#### ratings
* 10,000 entries
* Targeting book_id 1-5000
* rater: 1-30
* rating: 0|0.5|1|1.5|2|2.5|3|3.5|4|4.5|5
* date_rated: 12/01/2011 - 12/04/2014

#### list
* 500 entries
* Targeting user_id 1-30

#### book_list
* 10,000 entries
* Targeting book_id 1-5000
* Targeting list_id 1-500

#### user_log
* 5000 entries
* Targeting book_id 1-10000
* pages_read: 1-1000


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

