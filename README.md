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
2. Use python to execute load-template.py. This will parse and import all sample_data (**provided books.json, authors.json, & works.json should be in data/sample-data**). *TODO: When load-template.py is finalize, replace this step with a (chunkified?) SQL file for import.*
3. Execute data/starting_data.sql on the database to import generic starting manual and randomly generated data.


Sample Data Structure Information
------
From http://www.danneu.com/posts/authordb-datomic-tutorial/
```
There isn't much documentation to be found, but basically Open Library has a concept of:

Authors
Works
Editions
A Work is the abstract representation of a book. It at least has a title and a set of authors associated with it.

An Author can belong to many books.

An Edition is a concrete publication of a Work. It can contain things like publication dates and it can represent hardcover books, paperbacks, and ebooks. I didn't even crack open the edition data dump (ran out of hard-drive space) but I believe Editions can even have their own Authors.
```

So in our DDL we will most likely use the following mapping:
Works -> Book Core

#### Authors
Total Valid Rows:
| Key | Amount |



#### Works
Total Valid Rows:
| Key | Amount |


#### Books
Total Valid Rows:
| Key | Amount |