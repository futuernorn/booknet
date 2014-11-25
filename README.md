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


So in our DDL we will most likely use the following mapping:
Works -> Book Core

Not all data rows have all keys. Here is a breakdown of the total occurences of a given key. Only the more common keys are shown, a full breakdown is [here](doc/data_keys.md).
####Author Key Occurances

| Key | # |
| --- | --- |
| name_too_long | 0 |
| marc | 1 |
| subtitle | 1 |
| subject_time | 1 |
| genres | 1 |
| series | 1 |
| notes | 1 |
| website_name | 1 |
| create | 1 |
| subject_place | 2 |
| by_statement | 2 |
| title_prefix | 2 |
| tags | 3 |
| dewey_decimal_class | 3 |
| subjects | 4 |
| number_of_pages | 5 |
| publishers | 5 |
| authors | 5 |
| lc_classifications | 5 |
| source_records | 5 |
| languages | 5 |
| oclc_numbers | 5 |
| publish_country | 5 |
| publish_places | 5 |
| pagination | 5 |
| lccn | 5 |
| publish_date | 5 |
| numeration | 7 |
| role | 12 |
| photograph | 60 |
| entity_type | 71 |
| fuller_name | 178 |
| location | 182 |
| website | 211 |
| date | 469 |
| wikipedia | 506 |
| comment | 509 |
| links | 986 |
| bio | 1919 |
| title | 2999 |
| photos | 3500 |
| alternate_names | 6561 |
| death_date | 21629 |
| latest_revision | 29399 |
| created | 45863 |
| birth_date | 50717 |
| personal_name | 129425 |
| type | 179646 |
| revision | 179646 |
| last_modified | 179646 |
| key | 179646 |
| name | 179646 |



####Work Key Occurances

| Key | # |
| --- | --- |
| title_too_long | 0 |
| translated_titles | 1 |
| original_languages | 1 |
| cover_edition | 19 |
| works | 52 |
| links | 136 |
| number_of_editions | 209 |
| excerpts | 1292 |
| first_sentence | 2169 |
| description | 3019 |
| subtitle | 8748 |
| subject_times | 14317 |
| dewey_number | 16983 |
| subject_people | 20016 |
| lc_classifications | 28441 |
| subject_places | 53114 |
| covers | 54487 |
| first_publish_date | 59885 |
| subjects | 111842 |
| authors | 192633 |
| title | 194938 |
| latest_revision | 194940 |
| type | 194940 |
| revision | 194940 |
| last_modified | 194940 |
| key | 194940 |
| created | 194940 |



####Book Key Occurances

| Key | # |
| --- | --- |
| title_too_long | 0 |
| isbn | 1 |
| collections | 1 |
| purchase_url | 1 |
| create | 8 |
| isbn_odd_length | 14 |
| original_isbn | 27 |
| coverimage | 29 |
| translation_of | 40 |
| translated_from | 42 |
| language | 51 |
| scan_records | 82 |
| contributors | 239 |
| copyright_date | 265 |
| scan_on_demand | 438 |
| isbn_invalid | 638 |
| links | 687 |
| subject_times | 760 |
| subject_people | 865 |
| uri_descriptions | 2151 |
| uris | 2176 |
| subject_places | 2478 |
| work_title | 2651 |
| ia_loaded_id | 2794 |
| classifications | 4377 |
| ia_box_id | 4694 |
| work_titles | 4812 |
| first_sentence | 5147 |
| full_title | 5221 |
| url | 5341 |
| location | 5541 |
| oclc_number | 5998 |
| subject_time | 6931 |
| description | 7300 |
| table_of_contents | 8948 |
| genres | 13363 |
| ocaid | 16315 |
| other_titles | 22395 |
| title_prefix | 27222 |
| physical_dimensions | 28142 |
| weight | 28300 |
| subject_place | 30799 |
| edition_name | 43639 |
| dewey_decimal_class | 55175 |
| source_records | 56710 |
| covers | 58589 |
| series | 61815 |
| oclc_numbers | 69079 |
| physical_format | 70053 |
| isbn_13 | 74585 |
| contributions | 75503 |
| identifiers | 77822 |
| lccn | 94021 |
| subtitle | 99029 |
| lc_classifications | 110358 |
| notes | 116890 |
| isbn_10 | 125508 |
| by_statement | 126707 |
| pagination | 165160 |
| created | 168502 |
| subjects | 170825 |
| publish_country | 174075 |
| publish_places | 177624 |
| number_of_pages | 186510 |
| languages | 222925 |
| latest_revision | 226053 |
| publishers | 239877 |
| publish_date | 241640 |
| title | 249965 |
| work | 250000 |
| type | 250000 |
| revision | 250000 |
| last_modified | 250000 |
| key | 250000 |
| authors | 250000 |

