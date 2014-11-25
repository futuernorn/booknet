/* Updating to match our revised midterm report -William Howland*/
/* Latest revision: 11/12/2014*/

DROP TABLE IF EXISTS user_level CASCADE;
CREATE TABLE user_level(
  level_id SERIAL PRIMARY KEY,
  level_name VARCHAR(255) NOT NULL,
  level_description TEXT NOT NULL
);

DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user"(
user_id serial Primary Key	NOT NULL,
login_name varchar(255) NOT NULL,
email varchar(255) NOT NULL,
password varchar(255) NOT NULL,
level_id smallint NOT NULL REFERENCES user_level,
date_created timestamp NOT NULL,
is_active BOOLEAN NOT NULL
);


DROP TABLE IF EXISTS "subject_genre" CASCADE;
CREATE TABLE subject_genre(
subject_id serial Primary Key	NOT NULL,
subject_name varchar(255) NOT NULL
);

DROP TABLE IF EXISTS "series" CASCADE;
CREATE TABLE series(
series_id serial Primary Key	NOT NULL,
series_name varchar(50) NOT NULL
);

DROP TABLE IF EXISTS book_core CASCADE;
CREATE TABLE book_core(
core_id serial Primary Key	NOT NULL,
book_title VARCHAR(250) NOT NULL,
book_description TEXT NOT NULL,
edition VARCHAR(255) NOT NULL
);


DROP TABLE IF EXISTS book CASCADE;
DROP TABLE IF EXISTS books CASCADE;
CREATE TABLE books(
book_id serial PRIMARY KEY NOT NULL,
core_id INTEGER NOT NULL REFERENCES book_core,
publication_date TIMESTAMP,
ISBN varchar(20),
book_type varchar(255),
page_count INTEGER,
language varchar(255),
variation varchar(255),
cover_name varchar(255)
);

DROP TABLE IF EXISTS "review" CASCADE;
CREATE TABLE review(
review_id serial Primary Key	NOT NULL,
book_id bigint NOT NULL REFERENCES books,
reviewer bigint NOT NULL REFERENCES "user",
date_reviewed timestamp NOT NULL,
review_text text NOT NULL
);

DROP TABLE IF EXISTS "user_request" CASCADE;
CREATE TABLE user_request(
userreq_id serial Primary Key	NOT NULL,
request_id bigint NOT NULL,
requested_user bigint NOT NULL,
request_type varchar(50) NOT NULL,
request_text text NOT NULL
);


DROP TABLE IF EXISTS "book_categorization" CASCADE;
CREATE TABLE book_categorization(
categorize_id SERIAL PRIMARY KEY	NOT NULL,
core_id bigint NOT NULL REFERENCES book_core,
subject_id bigint NOT NULL REFERENCES subject_genre
);

DROP TABLE IF EXISTS "book_series" CASCADE;
CREATE TABLE book_series(
bookseries_id serial PRIMARY KEY NOT NULL,
core_id bigint NOT NULL REFERENCES book_core,
series_id bigint NOT NULL REFERENCES series
);

DROP TABLE IF EXISTS "publicist" CASCADE;
CREATE TABLE publicist(
publicist_id SERIAL PRIMARY KEY NOT NULL,
publicist_name VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS "book_publication" CASCADE;
CREATE TABLE book_publication(
publication_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES books,
publicist_id bigint NOT NULL REFERENCES publicist,
position smallint NOT NULL
);



DROP TABLE IF EXISTS "user_log" CASCADE;
CREATE TABLE user_log(
log_id serial NOT NULL,
book_id int NOT NULL,
reader int NOT NULL,
status int NOT NULL,
date_logged timestamp NOT NULL,
pages_read int NOT NULL,
log_text text NOT NULL
);



DROP TABLE IF EXISTS "tag" CASCADE;
CREATE TABLE tag(
tag_id serial PRIMARY KEY NOT NULL,
tag_name varchar(255) NOT NULL
);

DROP TABLE IF EXISTS "metaseries" CASCADE;
CREATE TABLE metaseries(
seriesmap_id SERIAL PRIMARY KEY NOT NULL,
metaseries bigint NOT NULL,
series bigint REFERENCES series
);

DROP TABLE IF EXISTS "follow" CASCADE;
CREATE TABLE follow(
follow_id serial PRIMARY KEY NOT NULL,
follower bigint NOT NULL REFERENCES "user",
user_followed bigint NOT NULL REFERENCES "user",
date_followed timestamp NOT NULL,
is_actively_followed BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS "institution" CASCADE;
CREATE TABLE institution(
institution_id SERIAL PRIMARY KEY NOT NULL,
institution_name VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS "author" CASCADE;
CREATE TABLE author(
author_id serial PRIMARY KEY NOT NULL,
author_name varchar(255) NOT NULL,
author_alias varchar(255) 
);

DROP TABLE IF EXISTS "authorship" CASCADE;
CREATE TABLE authorship(
authorship_id serial PRIMARY KEY NOT NULL,
core_id bigint NOT NULL REFERENCES book_core,
author_id INTEGER NOT NULL REFERENCES author,
institution_id bigint REFERENCES institution,
position smallint NOT NULL
);



DROP TABLE IF EXISTS "list" CASCADE;
CREATE TABLE list(
list_id serial PRIMARY KEY NOT NULL,
list_name varchar(255) NOT NULL,
user_id bigint NOT NULL REFERENCES "user",
date_created timestamp NOT NULL,
list_description text NOT NULL
);

DROP TABLE IF EXISTS "book_tag" CASCADE;
CREATE TABLE book_tag(
booktag_id serial PRIMARY KEY NOT NULL,
book_id int NOT NULL,
tag_id int NOT NULL
);

DROP TABLE IF EXISTS "bookmark" CASCADE;
CREATE TABLE bookmark(
bookmark_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES books,
reader bigint NOT NULL REFERENCES "user",
page_number varchar(7) NOT NULL,
date_marked TIMESTAMP NOT NULL,
is_retired BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS "user_profile" CASCADE;
CREATE TABLE user_profile(
user_id serial PRIMARY KEY NOT NULL,
property_id int NOT NULL,
property_value text NOT NULL,
private_indicator int NOT NULL
);



DROP TABLE IF EXISTS "book_list" CASCADE;
CREATE TABLE book_list(
booklist_id serial PRIMARY KEY NOT NULL,
list_id bigint NOT NULL REFERENCES list,
book_id bigint NOT NULL REFERENCES books,
date_added timestamp NOT NULL
);

DROP TABLE IF EXISTS "ratings" CASCADE;
CREATE TABLE ratings (
ratings serial PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES books,
rater bigint NOT NULL REFERENCES "user",
rating smallint NOT NULL,
date_rated timestamp NOT NULL
);

DROP TABLE IF EXISTS "profile_property" CASCADE;
CREATE TABLE profile_property(
property_id SERIAL PRIMARY KEY NOT NULL,
property_name varchar(255) NOT NULL,
prop_description bigint NOT NULL
);

DROP TABLE IF EXISTS "profile_map" CASCADE;
CREATE TABLE profile_map(
profile_map_id SERIAL PRIMARY KEY,
user_id bigint NOT NULL REFERENCES "user",
property_id bigint NOT NULL REFERENCES profile_property,
property_value VARCHAR(255) NOT NULL,
is_private BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS "user_lock" CASCADE;
CREATE TABLE user_lock(
lock_id serial PRIMARY KEY NOT NULL,
user_id bigint NOT NULL REFERENCES "user",
lock_date timestamp NOT NULL,
indefinite_ban boolean NOT NULL,
unlock_date timestamp NOT NULL,
moderator bigint NOT NULL
);

DROP TABLE IF EXISTS "request" CASCADE;
CREATE TABLE request(
request_id SERIAL PRIMARY KEY NOT NULL,
user_id bigint NOT NULL REFERENCES "user",
type VARCHAR(255) NOT NULL,
date_requested timestamp NOT NULL,
priority smallint NOT NULL,
status VARCHAR(255) NOT NULL,
date_of_status timestamp NOT NULL,
date_last_viewed timestamp NOT NULL,
moderator int NOT NULL,
moderator_notes text NOT NULL
);

DROP TABLE IF EXISTS "request_on_user" CASCADE;
CREATE TABLE request_on_user(
request_on_user_id SERIAL PRIMARY KEY,
request_id BIGINT NOT NULL,
request_user BIGINT NOT NULL,
request_type VARCHAR(255) NOT NULL,
request_text TEXT NOT NULL
);

DROP TABLE IF EXISTS "request_on_book" CASCADE;
CREATE TABLE request_on_book(
request_on_book_id SERIAL PRIMARY KEY NOT NULL,
request_id bigint NOT NULL REFERENCES Request,
book_id bigint NOT NULL REFERENCES books,
request_type varchar(255) NOT NULL,
request_text text NOT NULL
);

DROP TABLE IF EXISTS "permission" CASCADE;
CREATE TABLE permission(
 permission_id SERIAL PRIMARY KEY,
 perm_description TEXT NOT NULL
);

DROP TABLE IF EXISTS "permission_map" CASCADE;
CREATE TABLE permission_map(
 permission_map_id SERIAL PRIMARY KEY,
 level_id smallint NOT NULL REFERENCES user_level,
 permission_id smallint NOT NULL REFERENCES permission
);

DROP TABLE IF EXISTS "moderator_log" CASCADE;
CREATE TABLE moderator_log(
  moderator_log_id SERIAL PRIMARY KEY,
  moderator bigint NOT NULL,
  request_id bigint NOT NULL REFERENCES request,
  action VARCHAR(255) NOT NULL,
  action_date TIMESTAMP NOT NULL,
  log_description TEXT NOT NULL
);

DROP TABLE IF EXISTS "log" CASCADE;
CREATE TABLE "log"(
  log_id SERIAL PRIMARY KEY NOT NULL,
  user_id bigint NOT NULL REFERENCES "user",
  book_id bigint NOT NULL REFERENCES books,
  log_status varchar(255) NOT NULL,
  date_logged TIMESTAMP NOT NULL,
  pages_read integer NOT NULL,
  log_text TEXT NOT NULL
);

DROP TABLE IF EXISTS "book_search" CASCADE;
CREATE TABLE book_search(
book_search_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES books,
search_vector TSVECTOR NOT NULL
);

/*
CREATE INDEX */

/* Still a work in progress but I'll keep uploading it as I update it!*/
