CREATE TABLE "User"(
user_id serial Primary Key	NOT NULL,
login_name varchar(50) NOT NULL,
email varchar(50) NOT NULL,
password varchar(50) NOT NULL,
level_id bigint NOT NULL,
date_created timestamp NOT NULL
);

CREATE TABLE SubjectGenre(
subject_id serial Primary Key	NOT NULL,
subject_name varchar(50) NOT NULL
);

CREATE TABLE Series(
series_id serial Primary Key	NOT NULL,
series_name varchar(50) NOT NULL
);

CREATE TABLE Review(
review_id serial Primary Key	NOT NULL,
book_id bigint NOT NULL,
reviewer bigint NOT NULL,
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
book_title varchar(50) NOT NULL,
book_description text NOT NULL,
edition varchar(50) NOT NULL
);

CREATE TABLE BookCategorize(
categorize_id serial Primary Key	NOT NULL,
core_id bigint NOT NULL,
subject_id bigint NOT NULL
);

CREATE TABLE BookSeries(
bookseries_id serial Primary Key	NOT NULL,
core_id bigint NOT NULL,
series_id bigint NOT NULL
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
book_id serial NOT NULL,
core_id int NOT NULL,
publisher text NOT NULL,
publication_date timestamp NOT NULL,
ISBN varchar(50) NOT NULL,
book_type int NOT NULL,
page_count int NOT NULL,
language varchar(50) NOT NULL,
variation int NOT NULL
);

CREATE TABLE Tag(
tag_id serial NOT NULL,
tag_name varchar(50) NOT NULL
);

CREATE TABLE Follow(
follow_id serial NOT NULL,
follower int NOT NULL,
user_followed int NOT NULL,
date_followed timestamp NOT NULL,
active_indicator smallint NOT NULL
);

CREATE TABLE Authorship(
authorship_id serial NOT NULL,
core_id int NOT NULL,
author_id int NOT NULL,
position smallint NOT NULL
);

CREATE TABLE List(
list_id serial NOT NULL,
list_name varchar(50) NOT NULL,
user_id int NOT NULL,
date_created timestamp NOT NULL,
list_description text NOT NULL
);

CREATE TABLE BookTag(
booktag_id serial NOT NULL,
book_id int NOT NULL,
tag_id int NOT NULL
);

CREATE TABLE UserProfile(
user_id serial NOT NULL,
property_id int NOT NULL,
property_value text NOT NULL,
private_indicator int NOT NULL
);

CREATE TABLE Author(
author_id serial NOT NULL,
author_name varchar(50) NOT NULL,
author_alias varchar(50) NOT NULL,
institution int NOT NULL
);

CREATE TABLE BookList(
booklist_id serial NOT NULL,
list_id int NOT NULL,
book_id int NOT NULL,
date_added timestamp NOT NULL
);

CREATE TABLE Rate(
rate_id serial NOT NULL,
book_id int NOT NULL,
rater int NOT NULL,
rating smallint NOT NULL,
date_rated timestamp NOT NULL
);

CREATE TABLE ProfileProperty(
property_id serial NOT NULL,
property_name varchar(50) NOT NULL
);

CREATE TABLE UserLock(
lock_id serial NOT NULL,
user_id int NOT NULL,
lock_date timestamp NOT NULL,
indefinite_ban boolean NOT NULL,
unlock_date timestamp NOT NULL,
moderator int NOT NULL
);

CREATE TABLE Request(
request_id serial NOT NULL,
user_id int NOT NULL,
date_requested timestamp NOT NULL,
priority smallint NOT NULL,
status smallint NOT NULL,
status_date timestamp NOT NULL,
last_viewed_date timestamp NOT NULL,
moderator int NOT NULL,
mod_comments text NOT NULL
);

CREATE TABLE BookRequest(
bookreq_id serial NOT NULL,
requeust_id int NOT NULL,
book_id int NOT NULL,
request_type smallint NOT NULL,
request_text text NOT NULL,
modlog_id int NOT NULL,
moderator int NOT NULL,
request_id int NOT NULL,
action_type smallint NOT NULL,
action_date timestamp NOT NULL,
description text NOT NULL);