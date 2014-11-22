#!/usr/bin/env python

import json
import operator
import re


'''
e.g.:
{"name": "William York Tindall",
"created": {"type": "/type/datetime", "value": "2008-04-01T03:28:50.625462"},
"death_date": "1981",
"last_modified": {"type": "/type/datetime", "value": "2010-04-10T23:35:59.317184"},
"latest_revision": 3,
"key": "/authors/OL529081A",
"birth_date": "1903",
"personal_name": "William York Tindall",
"type": {"key": "/type/author"},
"revision": 3}

'''
with open('data/sample-data/authors.json') as af:
    count = 1
    for line in af:
        if count > 1:
            break
        count += 1
        author = json.loads(line.strip())
        author_key = author['key']
        # print 'found author', author_key
        # put the author in your database
'''

{
   "lc_classifications":[
      "QM421 .P3"
   ],
   "last_modified":{
      "type":"/type/datetime",
      "value":"2010-12-04T08:55:43.987678"
   },

{
   "lc_classifications":[
      "GB701 .W375 no. 03-4323",
      "GB842 .W375 no. 03-4323"
   ],
   "last_modified":{
      "type":"/type/datetime",
      "value":"2012-08-08T06:04:17.339243"
   },
   "title":"Hydrologic effects of the 1988 Galena Fire, Black Hills area, South Dakota",
   "created":{
      "type":"/type/datetime",
      "value":"2009-12-10T00:00:08.283396"
   },
   "subject_places":[
      "Black Hills (S.D. and Wyo.)",
      "Custer State Park",
      "Custer State Park (S.D.)",
      "Custer State Park Region",
      "South Dakota"
   ],
   "first_publish_date":"2004",
   "latest_revision":6,
   "key":"/works/OL2584786W",
   "authors":[
      {
         "type":{
            "key":"/type/author_role"
         },
         "author":{
            "key":"/authors/OL370399A"
         }
      }
   ],
   "dewey_number":[
      "553.7/0973 s",
      "551.48/09783/9"
   ],
   "type":{
      "key":"/type/work"
   },
   "subjects":[
      "Environmental aspects",
      "Environmental aspects of Forest fires",
      "Forest Hydrology",
      "Forest fires",
      "Hydrology, Forest",
      "Streamflow",
      "Forest hydrology"
   ],
   "revision":6
}
'''
work_keys = {'title_too_long':0}
with open('data/sample-data/works.json') as af:
    for line in af:
        work = json.loads(line.strip())
        work_key = work['key']
        #print 'found work', work_key
        # put the work in your database
        for key in work:
            try:
                work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] += 1
            except KeyError:
                work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] = 1
            # first clean up book title
        try:
            work['title'] = work['title'].strip().encode('ascii', 'xmlcharrefreplace')
        except KeyError:
            print "No title for this book entry! Continuing..."
            continue
            

        if len(work['title']) > 250:
            #print "This work's title (%s) is too long, not importing it for the moment! Continuing..." % work['title']
            work_keys['title_too_long'] += 1
            continue

            # now check to see if we have an existing "book_core" entry
            #print "Checking to see if a book core entry exists for %s..." % works['title']
            #cur.execute('''
            #    SELECT core_id
            #    FROM book_core
            #    WHERE book_title = %s
            #''', (work['title'],))

           # if (cur.rowcount != 1):
           #print "No book core entry found, adding one now..."
           #too many, or no, matching book_core entries found -> make a new one
           #cur.execute('''
           #  INSERT INTO book_core (book_title, book_description, edition)
           #  VALUES(%s, %s, %s)
           #  RETURNING core_id
           #''', (book['title'], '', book['revision']))

            # Retrieve book_core_id for book insertion
            # book_core_id = cur.fetchone()[0]
            book_core_id = 1
            #print "Book core ID obtained: %s!" % book_core_id

            # add author relationships if found
        try:
            for author in work['authors']:
                position = 1
                    #cur.execute('''
                    #SELECT author_id
                    #FROM author
                    #WHERE author_alias = %s
                    #''', (author,))
        except KeyError:
            #print "No authors found!"
            pass

    #    print "-----------------------\n\n"
    sorted_work_keys = sorted(work_keys.items(), key=operator.itemgetter(1))
    #print sorted_work_keys
    for x in sorted_work_keys:
        print x[0], x[1]


with open('data/sample-data/books.json') as af:
    count = 1
    for line in af:
        if count > 1:
            break
        count += 1
        book = json.loads(line.strip())
        book_key = book['key']
        # print 'found book', book_key
        # print book
        # put the book in your database
