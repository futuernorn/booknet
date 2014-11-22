#!/usr/bin/env python

import json
import easypg
import operator
import re

easypg.config_name = 'bookserver'

author_keys = {'name_too_long':0}
work_keys = {'title_too_long':0}
book_keys = {'title_too_long':0}

LOOP_LIMIT = False

log_file = open('load-template.log', 'w')


author_ids = {}
work_ids = {}

# covers mapped to book_core.core_id for potential later use
work_covers = {}
with open('data/sample-data/authors.json') as af:
    count = 1
    for line in af:
        if LOOP_LIMIT and (count > 1):
            break
        count += 1
        author = json.loads(line.strip())
        author_key = author['key']
        for key in author:
            try:
                author_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] += 1
                # if isinstance(val, dict):
                #     for inner_key in val:
                #         try:
                #             author_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] += 1
                #         except KeyError:
                #             author_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] = 1

            except KeyError:
                author_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] = 1
        # print 'found author', author_key
        # put the author in your database
        with easypg.cursor() as cur:
            # first clean up book title
            try:
                author['name'] = author['name'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                print >> log_file, "No name for this author entry! Continuing..."
                continue


            if len(author['name']) > 255:
                print >> log_file, "This author's name (%s) is too long, not importing it for the moment! Continuing..." % author['name']
                continue
            try:
                author['personal_name'] = author['personal_name'].strip().encode('ascii', 'xmlcharrefreplace')
                if len(author['personal_name']) > 255:
                    print >> log_file, "This author's key (%s) is too long, not importing it for the moment! Continuing..." % author['key']
                    continue
            except KeyError:
                author['personal_name'] = ''
            # now check to see if we have an existing "author" entry


            # print "Inserting author name  %s along with key %s." % (author['name'], author['key'])
            cur.execute('''
              INSERT INTO author (author_name, author_alias)
              VALUES(%s, %s)
              RETURNING author_id
            ''', (author['name'], author['personal_name']))
            if cur.rowcount == 1:
                author_ids[author['key']] = cur.fetchone()[0]
                print >> log_file, "Inserted author name  %s along with alias %s, represented by author_id: %s." % (author['name'], author['personal_name'], author_ids[author['key']])

            print >> log_file, "-----------------------\n\n"


with open('data/sample-data/works.json') as af:
    book_covers = open('cover_ids.json', 'w')
    count = 1
    for line in af:
        if LOOP_LIMIT and (count > 1):
            break
        count += 1
        work = json.loads(line.strip())
        work_key = work['key']
        #print 'found work', work_key
        # put the work in your database
        for key in work:
            try:
                work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] += 1
                # if isinstance(val, dict):
                #     for inner_key in val:
                #         try:
                #             work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] += 1
                #         except KeyError:
                #             work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] = 1

            except KeyError:
                work_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] = 1
            # first clean up book title
        try:
            work['title'] = work['title'].strip().encode('ascii', 'xmlcharrefreplace')
        except KeyError:
            print >> log_file, "No title for this book work! Continuing..."
            continue
        with easypg.cursor() as cur:
            # first clean up book title
            try:
                work['title'] = work['title'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                print >> log_file, "No title for this book entry! Continuing..."
                continue

            if len(work['title']) > 250:
                print >> log_file, "This work's title (%s) is too long, not importing it for the moment! Continuing..." % work['title']
                continue

            try:
                work['description'] = work['description'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                work['description'] = ""
            except AttributeError:
                # print to error log later
                pass

            # now check to see if we have an existing "book_core" entry
            #print "Checking to see if a book core entry exists for %s..." % works['title']
            cur.execute('''
                SELECT core_id
                FROM book_core
                WHERE book_title = %s
            ''', (work['title'],))

            if (cur.rowcount != 1):
                print >> log_file, "No book core entry found, adding one now..."
                #too many, or no, matching book_core entries found -> make a new one
                print >> log_file, "Inserting work / book core: %s." % (work['title'])
                cur.execute('''
                  INSERT INTO book_core (book_title, book_description, edition)
                  VALUES(%s, %s, %s)
                  RETURNING core_id
                ''', (work['title'], work['description'], 1))

            # Retrieve book_core_id for book insertion
            book_core_id = cur.fetchone()[0]

            # map to book_tag
            # e.g., "subjects": ["Environmental aspects", "Environmental aspects of Forest fires", "Forest Hydrology",
            # "Forest fires", "Hydrology, Forest", "Streamflow", "Forest hydrology"]
            # work['subjects']

            # locations related to work/book?
            # e.g.,  "subject_places": ["Black Hills (S.D. and Wyo.)", "Custer State Park",
            # "Custer State Park (S.D.)", "Custer State Park Region", "South Dakota"]
            # work['subject_places']

            try:
                work_covers[book_core_id] = work['covers']
            except KeyError:
                # No covers here
                pass

            # add author relationships if found
            try:
                for author in work['authors']:
                    author = author[key]
                    position = 1
                    try:
                        print >> log_file, author
                        author_id = author_ids[author]
                        cur.execute('''
                        INSERT INTO authorship (core_id, author_id, position)
                        VALUES(%s, %s)
                        RETURNING author_id
                        ''', (book_core_id, author_id, position))
                        position += 1
                    except KeyError:
                        print >> log_file, "Couldn't find an author_id entry for author key: %s..." % author
            except KeyError:
                print >> log_file, "No authors found!"

            # print >> log_file, "-----------------------\n\n"
    json.dump(work_covers, book_covers)
    book_covers.close()



with open('data/sample-data/books.json') as af:
    count = 1
    for line in af:
        if LOOP_LIMIT and (count > 2000):
            break
        count += 1
        book = json.loads(line.strip())
        book_key = book['key']
        for key in book:
            try:
                book_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] += 1
                # if isinstance(val, dict):
                #     for inner_key in val:
                #         try:
                #             book_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] += 1
                #         except KeyError:
                #             book_keys[key.strip().encode('ascii', 'xmlcharrefreplace')+"_"+inner_key] = 1

            except KeyError:
                book_keys[key.strip().encode('ascii', 'xmlcharrefreplace')] = 1
        # print 'found book', book_key
        # print book
        # put the book in your database
        with easypg.cursor() as cur:
            # first clean up book title
            try:
                book['title'] = book['title'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                # should be output to error log 
                #print "No title for this book entry! Continuing..."
                continue


            if len(book['title']) > 250:
                # log this latter
                #print "This book's title (%s) is too long, not importing it for the moment! Continuing..." % book['title']
                continue

            # now check to see if we have an existing "book_core" entry
            print >> log_file, "Checking to see if a book core entry exists for %s..." % book['title']
            try:
                book_core_id = work_ids[book['work']]
                print >> log_file, "Book core ID obtained: %s!" % book_core_id
            except KeyError:

                # cur.execute('''
                #     SELECT core_id
                #     FROM book_core
                #     WHERE book_title = %s
                # ''', (book['title'],))

                # if (cur.rowcount != 1):
                print >> log_file, "No book core entry found (work_ids[%s]), adding one now..." % book['work']
                #too many, or no, matching book_core entries found -> make a new one
                cur.execute('''
                  INSERT INTO book_core (book_title, book_description, edition)
                  VALUES(%s, %s, %s)
                  RETURNING core_id
                ''', (book['title'], '', book['revision']))

                # Retrieve book_core_id for book insertion
                book_core_id = cur.fetchone()[0]



            # check to see what type of ISBN we have to work with, go with ISBN if possible
            # explanation of this type of structure at: http://stackoverflow.com/a/1592578/1431509
            try:
                book['isbn_13']
            except KeyError:
                try:
                    book['isbn_10']
                except KeyError:
                    print >> log_file, "%s has no ISBN!" % book['title']
                    book_isbn = []
                else:
                    book_isbn = book['isbn_10']
            else:
                book_isbn = book['isbn_13']

            try:
                book['number_of_pages']
            except KeyError:
                page_count = None
                print >> log_file, "%s has no page count!" % book['title']
            else:
                page_count = book['number_of_pages']

            try:
                book['physical_format']
            except KeyError:
                book_type = None
            else:
                book_type = book['physical_format']

            try:
                print >> log_file, "Publish date is: %s." % book['publish_date']
                original_date = book['publish_date']
            except KeyError:
                print >> log_file, "%s has no publication date!" % book['title']
                publication_date = None
                original_date = None
            except UnicodeEncodeError:
                # log this later
                pass
            else:
                if re.match('\w* \d{1,2}, \d{4}', book['publish_date']):
                    m = re.match('(\w* \d{1,2}, \d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = m.groups()[0]
                elif re.match('\w* \d{4}', book['publish_date']):
                    m = re.match('(\w*) (\d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = "%s 01, %s" % (m.groups()[0], m.groups()[1])
                elif re.match('\d{4}', book['publish_date']):
                    m = re.match('(\d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = "January 01, %s" % m.groups()[0]
                else :
                    publication_date = None
            print >> log_file, "Parsed publication_date is: %s (Original date: %s)." % (publication_date, original_date)
            # was getting output in this formatting "[u'9780110827667']" slicing off the excess
            # until I find whats going on
            # book_isbn = book_isbn[2:-2]
            for isbn in book_isbn:
                isbn = ''.join(x for x in isbn if x.isdigit())
                print >> log_file, "Inserting book title %s along with core_id %s (ISBN: %s - Date: %s)." % (book['title'], book_core_id, isbn, publication_date)
                cur.execute('''
                    INSERT INTO books (core_id, publication_date, isbn, book_type, page_count)
                    VALUES(%s, %s, %s, %s, %s)
                ''', (book_core_id, publication_date, isbn, book_type, page_count))

            # add author relationships if found
            position = 1
            try:

                for author in book['authors']:
                    position += 1
                    try:
                        author_id = author_ids[author]
                        cur.execute('''
                        INSERT INTO authorship (core_id, author_id, position)
                        VALUES(%s, %s)
                        RETURNING author_id
                        ''', (book_core_id, author_id, position))
                        position += 1
                    except KeyError:
                        print >> log_file, "KeyError: Couldn't find an author_id entry for author key: %s..." % author
                    except TypeError:
                        print >> log_file, "TypeError: Couldn't find an author_id entry for author key: %s..." % author
            except KeyError:
                print >> log_file, "No authors found!"

            print >> log_file, "-----------------------\n\n"



sorted_author_keys = sorted(author_keys.items(), key=operator.itemgetter(1))
sorted_work_keys = sorted(work_keys.items(), key=operator.itemgetter(1))
sorted_book_keys = sorted(book_keys.items(), key=operator.itemgetter(1))

print "***** Author Key Occurances"
print "| Key | # |"
for x in sorted_author_keys:
    print "| %s | %s |" % (x[0], x[1])
print "-----------------------\n\n"


print "***** Work Key Occurances"
print "| Key | # |"
for x in sorted_work_keys:
    print "| %s | %s |" % (x[0], x[1])
print "-----------------------\n\n"


print "***** Book Key Occurances"
print "| Key | # |"
for x in sorted_book_keys:
    print "| %s | %s |" % (x[0], x[1])
print "-----------------------\n\n"

log_file.close()
