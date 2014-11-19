/* Updating to match our revised midterm report -William Howland*/
/* Latest revision: 11/12/2014*/

CREATE TABLE "User"(
user_id serial Primary Key	NOT NULL,
login_name varchar(255) NOT NULL,
email varchar(255) NOT NULL,
password varchar(255) NOT NULL,
level_id smallint NOT NULL REFERENCES UserLevel,
date_created timestamp NOT NULL,
is_active BOOLEAN NOT NULL
);

CREATE TABLE UserLevel(
  level_id SERIAL PRIMARY KEY,
  level_name VARCHAR(255) NOT NULL,
  level_description TEXT NOT NULL
);

CREATE TABLE SubjectGenre(
subject_id serial Primary Key	NOT NULL,
subject_name varchar(255) NOT NULL
);

CREATE TABLE Series(
series_id serial Primary Key	NOT NULL,
series_name varchar(50) NOT NULL
);

CREATE TABLE Review(
review_id serial Primary Key	NOT NULL,
book_id bigint NOT NULL REFERENCES Book,
reviewer bigint NOT NULL REFERENCES "User",
date_reviewed timestamp NOT NULL,
review_text text NOT NULL
);

CREATE TABLE UserRequest(
userreq_id serial Primary Key	NOT NULL,
request_id bigint NOT NULL,
requested_user bigint NOT NULL,
request_type varchar(50) NOT NULL,
request_text text NOT NULL
);

CREATE TABLE BookCore(
core_id serial Primary Key	NOT NULL,
book_title varchar(255) NOT NULL REFERENCES Book,
book_description text NOT NULL,
edition varchar(255) NOT NULL
);

CREATE TABLE BookCategorization(
categorize_id SERIAL PRIMARY KEY	NOT NULL,
core_id bigint NOT NULL REFERENCES BookCore,
subject_id bigint NOT NULL REFERENCES SubjectGenre
);

CREATE TABLE BookSeries(
bookseries_id serial PRIMARY KEY NOT NULL,
core_id bigint NOT NULL REFERENCES BookCore,
series_id bigint NOT NULL REFERENCES Series
);

CREATE TABLE BookPublication(
publication_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES Book,
publicist_id bigint NOT NULL REFERENCES Publicist,
position smallint NOT NULL
);

CREATE TABLE Publicist(
publicist_id SERIAL PRIMARY KEY NOT NULL,
publicist_name VARCHAR(255) NOT NULL
);

CREATE TABLE UserLog(
log_id serial NOT NULL,
book_id int NOT NULL,
reader int NOT NULL,
status int NOT NULL,
date_logged timestamp NOT NULL,
pages_read int NOT NULL,
log_text text NOT NULL
);

CREATE TABLE Book(
book_id serial PRIMARY KEY NOT NULL,
core_id varchar(255) NOT NULL REFERENCES BookCore,
publication_date TIMESTAMP NOT NULL,
ISBN varchar(13) NOT NULL,
book_type varchar(255) NOT NULL,
page_count integer NOT NULL,
language varchar(255) NOT NULL,
variation varchar(255) NOT NULL,
picture bytea NOT NULL
);

CREATE TABLE Tag(
tag_id serial PRIMARY KEY NOT NULL,
tag_name varchar(255) NOT NULL
);

CREATE TABLE Metaseries(
seriesmap_id SERIAL PRIMARY KEY NOT NULL,
metaseries bigint NOT NULL,
series bigint REFERENCES Series
);

CREATE TABLE Follow(
follow_id serial PRIMARY KEY NOT NULL,
follower bigint NOT NULL REFERENCES "User",
user_followed bigint NOT NULL REFERENCES "User",
date_followed timestamp NOT NULL,
is_actively_followed BOOLEAN NOT NULL
);

CREATE TABLE Authorship(
authorship_id serial PRIMARY KEY NOT NULL,
core_id bigint NOT NULL REFERENCES BookCore,
author_id VARCHAR(255) NOT NULL REFERENCES Author,
institution_id bigint NOT NULL REFERENCES Institution,
position smallint NOT NULL
);

CREATE TABLE Institution(
institution_id SERIAL PRIMARY KEY NOT NULL,
institution_name VARCHAR(255) NOT NULL
);

CREATE TABLE List(
list_id serial PRIMARY KEY NOT NULL,
list_name varchar(255) NOT NULL,
user_id bigint NOT NULL REFERENCES "User",
date_created timestamp NOT NULL,
list_description text NOT NULL
);

CREATE TABLE BookTag(
booktag_id serial PRIMARY KEY NOT NULL,
book_id int NOT NULL,
tag_id int NOT NULL
);

CREATE TABLE Bookmark(
bookmark_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES Book,
reader bigint NOT NULL REFERENCES "User",
page_number varchar(7) NOT NULL,
date_marked TIMESTAMP NOT NULL,
is_retired BOOLEAN NOT NULL
);

CREATE TABLE UserProfile(
user_id serial PRIMARY KEY NOT NULL,
property_id int NOT NULL,
property_value text NOT NULL,
private_indicator int NOT NULL
);

CREATE TABLE Author(
author_id serial PRIMARY KEY NOT NULL,
author_name varchar(255) NOT NULL,
author_alias varchar(255) NOT NULL
);

CREATE TABLE BookList(
booklist_id serial PRIMARY KEY NOT NULL,
list_id bigint NOT NULL REFERENCES List,
book_id bigint NOT NULL REFERENCES Book,
date_added timestamp NOT NULL
);

CREATE TABLE Rate(
rate_id serial PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES Book,
rater bigint NOT NULL REFERENCES "User",
rating smallint NOT NULL,
date_rated timestamp NOT NULL
);

CREATE TABLE ProfileProperty(
property_id SERIAL PRIMARY KEY NOT NULL,
property_name varchar(255) NOT NULL,
prop_description bigint NOT NULL
);

CREATE TABLE ProfileMap(
profilemap_id SERIAL PRIMARY KEY,
user_id bigint NOT NULL REFERENCES "User",
property_id bigint NOT NULL REFERENCES ProfileProperty,
property_value VARCHAR(255) NOT NULL,
is_private BOOLEAN NOT NULL
);

CREATE TABLE UserLock(
lock_id serial PRIMARY KEY NOT NULL,
user_id bigint NOT NULL REFERENCES "User",
lock_date timestamp NOT NULL,
indefinite_ban boolean NOT NULL,
unlock_date timestamp NOT NULL,
moderator bigint NOT NULL
);

CREATE TABLE Request(
request_id SERIAL PRIMARY KEY NOT NULL,
user_id bigint NOT NULL REFERENCES "User",
type VARCHAR(255) NOT NULL,
date_requested timestamp NOT NULL,
priority smallint NOT NULL,
status VARCHAR(255) NOT NULL,
date_of_status timestamp NOT NULL,
date_last_viewed timestamp NOT NULL,
moderator int NOT NULL,
moderator_notes text NOT NULL
);

CREATE TABLE RequestOnUser(
userrequest_id SERIAL PRIMARY KEY,
request_id BIGINT NOT NULL,
request_user BIGINT NOT NULL,
request_type VARCHAR(255) NOT NULL,
request_text TEXT NOT NULL
);

CREATE TABLE RequestOnBook(
bookrequest_id SERIAL PRIMARY KEY NOT NULL,
request_id bigint NOT NULL REFERENCES Request,
book_id bigint NOT NULL REFERENCES Book,
request_type varchar(255) NOT NULL,
request_text text NOT NULL
);

CREATE TABLE Permission(
 permission_id SERIAL PRIMARY KEY,
 perm_description TEXT NOT NULL
);

CREATE TABLE permissionMap(
 permmap_id SERIAL PRIMARY KEY,
 level_id smallint NOT NULL REFERENCES userLevel,
 permission_id smallint NOT NULL REFERENCES Permission
);

CREATE TABLE ModeratorLog(
  modlog_id SERIAL PRIMARY KEY,
  moderator bigint NOT NULL,
  request_id bigint NOT NULL REFERENCES Request,
  action VARCHAR(255) NOT NULL,
  action_date TIMESTAMP NOT NULL,
  log_description TEXT NOT NULL
);

CREATE TABLE "Log"(
  log_id SERIAL PRIMARY KEY NOT NULL,
  user_id bigint NOT NULL REFERENCES "User",
  book_id bigint NOT NULL REFERENCES Book,
  log_status varchar(255) NOT NULL,
  date_logged TIMESTAMP NOT NULL,
  pages_read integer NOT NULL,
  log_text TEXT NOT NULL
);

CREATE TABLE BookSearch(
bksrc_id SERIAL PRIMARY KEY NOT NULL,
book_id bigint NOT NULL REFERENCES Book,
search_vector TSVECTOR NOT NULL
);

/*
CREATE INDEX */

/* Still a work in progress but I'll keep uploading it as I update it!*/