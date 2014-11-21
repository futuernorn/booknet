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