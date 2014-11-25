#!/usr/bin/env python

import json
import easypg
import operator
import re
import sys, traceback
easypg.config_name = 'bookserver'


# Count the occurrences of any given key for a dataset
author_keys = {'name_too_long':0}
work_keys = {'title_too_long':0}
book_keys = {'title_too_long':0}

# Parse smaller chunks of data during some troubleshooting
IS_LOOP_LIMIT = True
#IS_LOOP_LIMIT = False
LOOP_LIMIT = 500
loop_counter = 0

LOGGING = True

log_file = open('load-template.log', 'w')
error_log = open('load-template-errors.log', 'w')

author_ids = {}
work_ids = {}
subject_ids = {}

# covers mapped to book_core.core_id for potential later use
work_covers = {}

def print_log_entry(log_file, message):
  if LOGGING:
    try:
        print >> log_file, message
    except:
        e = sys.exc_info()[0]
        traceback.print_exc(file=error_log)
        print >> log_file, "Big time error! %s" % e

def print_key_occurrences(heading, output, sorted_keys):
    max_occurrences = sorted_author_keys[0][1]
    display_cutoff = max_occurrences / 2
    print >> output, "####%s Occurrences (>%s)" % (heading,display_cutoff)
    print >> output, "| Key | # | Mapping |"
    print >> output, "| ---- | ---- | ---- |"
    for x in sorted_keys:
        if x[1] > display_cutoff:
            print >> output, "| %s | %s |" % (x[0], x[1])
    print >> output, "\n"

    print >> output, "####%s Occurrences (all)" % (heading)
    print >> output, "| Key | # | Mapping |"
    print >> output, "| ---- | ---- | ---- |"
    for x in sorted_keys:
        print >> output, "| %s | %s |" % (x[0], x[1])
    print >> output, "\n"

try:
    with open('data/sample-data/authors.json') as af:
        loop_counter = 0
        for line in af:
            if IS_LOOP_LIMIT and (loop_counter > LOOP_LIMIT):
              break
            loop_counter += 1
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
                    print_log_entry(error_log,"No name for this author entry (%s) ! Continuing..." % loop_counter)
                    continue


                if len(author['name']) > 255:
                    print_log_entry(error_log,"This author's name (%s) is too long, not importing it for the moment! Continuing..." % author['name'])
                    author_keys['name_too_long'] += 1
                    continue
                try:
                    author['personal_name'] = author['personal_name'].strip().encode('ascii', 'xmlcharrefreplace')
                    if len(author['personal_name']) > 255:
                        print_log_entry(error_log,"This author's personal_name (%s) is too long, not importing it for the moment! Continuing..." % author['key'])
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
                    print_log_entry(log_file,"Inserted author name  %s along with alias %s, represented by author_id: %s." % (author['name'], author['personal_name'], author_ids[author['key']]))


    book_covers = open('cover_ids.json', 'w')
    with open('data/sample-data/works.json') as af:

        loop_counter = 0
        for line in af:
            if IS_LOOP_LIMIT and (loop_counter > LOOP_LIMIT):
                break
            loop_counter += 1
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

            with easypg.cursor() as cur:
                try:
                    work['title'] = work['title'].strip().encode('ascii', 'xmlcharrefreplace')
                    if len(work['title']) > 250:
                        work_keys['title_too_long'] += 1
                        print_log_entry(error_log,"This work's title (%s) is too long, not importing it for the moment! Continuing..." % work['title'])
                        continue
                except KeyError:
                    print_log_entry(error_log,"No title for this work (%s)! Continuing..." % loop_counter)
                    continue

                try:
                    work['description'] = work['description'].strip().encode('ascii', 'xmlcharrefreplace')
                except KeyError:
                    work['description'] = ""
                except AttributeError:
                    # print to error log later.
                    work['description'] = ""
                    print_log_entry(error_log,"Can't use description, AttributeError (%s)." % loop_counter)
                    pass

                # now check to see if we have an existing "book_core" entry
                #print "Checking to see if a book core entry exists for %s..." % works['title']
                cur.execute('''
                    SELECT core_id
                    FROM book_core
                    WHERE book_title = %s
                ''', (work['title'],))

                if cur.rowcount != 1:
                    print_log_entry(log_file,"No book core entry found, adding one now...")
                    #too many, or no, matching book_core entries found -> make a new one
                    print_log_entry(log_file,"Inserting work / book core: %s :: %s." % (work['title'], loop_counter))
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
                # print "Work['covers']: %s" % work['covers']
                try:
                  for cover in work['covers']:
                    print cover
                    try:
                      work_covers[book_core_id].append(cover)
                    except:
                      work_covers[book_core_id] = []
                      work_covers[book_core_id].append(cover)
                except KeyError:
                    # No covers here
                    print_log_entry(error_log,"No covers found for %s" % loop_counter)
                    pass

                # add author relationships if found
                try:
                    for author in work['authors']:
                        author = author[key]
                        position = 1
                        try:
                            print_log_entry(log_file,author)
                            author_id = author_ids[author]
                            cur.execute('''
                            INSERT INTO authorship (core_id, author_id, position)
                            VALUES(%s, %s, %s)
                            RETURNING author_id
                            ''', (book_core_id, author_id, position))
                            position += 1
                        except KeyError:
                            print_log_entry(error_log,"Couldn't find an author_id entry for author key: %s..." % author)
                except KeyError:
                    print_log_entry(error_log,"No authors found (%s)!" % loop_counter)



    json.dump(work_covers, book_covers)
    book_covers.close()



    with open('data/sample-data/books.json') as af:
        loop_counter = 0
        for line in af:
            if IS_LOOP_LIMIT and (loop_counter > LOOP_LIMIT):
                break
            loop_counter += 1
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
                    print_log_entry(error_log,"No title for this book entry (%s) ! Continuing..." % loop_counter)
                    continue


                if len(book['title']) > 250:
                    # log this latter
                    book_keys['title_too_long'] += 1
                    print_log_entry(error_log,"This book's title (%s) is too long, not importing it for the moment! Continuing..." % book['title'])
                    continue

                # now check to see if we have an existing "book_core" entry
                print_log_entry(log_file,"Checking to see if a book core entry exists for %s..." % book['title'])
                try:
                    book_core_id = work_ids[book['work']]
                    print_log_entry(log_file,"Book core ID obtained: %s!" % book_core_id)
                except KeyError:

                    # cur.execute('''
                    #     SELECT core_id
                    #     FROM book_core
                    #     WHERE book_title = %s
                    # ''', (book['title'],))

                    # if (cur.rowcount != 1):
                    print_log_entry(error_log,"No book core entry found (work_ids[%s]), adding one now..." % book['work'])
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
                        print_log_entry(error_log,"%s has no ISBN!" % book['title'])
                        book_isbn = []
                    else:
                        book_isbn = book['isbn_10']
                else:
                    book_isbn = book['isbn_13']

                try:
                    book['number_of_pages']
                except KeyError:
                    page_count = None
                    print_log_entry(error_log,"%s has no page count!" % book['title'])
                else:
                    page_count = book['number_of_pages']

                try:
                    book['physical_format']
                except KeyError:
                    book_type = None
                else:
                    book_type = book['physical_format']

                try:
                    print_log_entry(log_file,"Publish date is: %s." % book['publish_date'])
                    original_date = book['publish_date']
                except KeyError:
                    print_log_entry(error_log,"%s has no publication date!" % book['title'])
                    publication_date = None
                    original_date = None
                except UnicodeEncodeError:
                    print_log_entry(error_log,"UnicodeEncodeError for publish_date (%s)?" % loop_counter)
                    pass
                else:
                    if re.match('\w* \d{1,2}, \d{4}', book['publish_date']):
                        m = re.match('(\w* \d{1,2}, \d{4})', book['publish_date'])
                        publication_date = m.groups()[0]
                    elif re.match('\w* \d{4}', book['publish_date']):
                        m = re.match('(\w*) (\d{4})', book['publish_date'])
                        publication_date = "%s 01, %s" % (m.groups()[0], m.groups()[1])
                    elif re.match('\d{4}', book['publish_date']):
                        m = re.match('(\d{4})', book['publish_date'])
                        publication_date = "January 01, %s" % m.groups()[0]
                    else :
                        publication_date = None
                print_log_entry(log_file,"Parsed publication_date is: %s (Original date: %s)." % (publication_date, original_date))
                # was getting output in this formatting "[u'9780110827667']" slicing off the excess
                # until I find whats going on
                # book_isbn = book_isbn[2:-2]
                for isbn in book_isbn:
                    isbn = ''.join(x for x in isbn if x.isdigit())
                    print_log_entry(log_file,"Inserting book title %s along with core_id %s (ISBN: %s - Date: %s)." % (book['title'], book_core_id, isbn, publication_date))
                    cur.execute('''
                        INSERT INTO books (core_id, publication_date, isbn, book_type, page_count)
                        VALUES(%s, %s, %s, %s, %s)
                        RETURNING book_id
                    ''', (book_core_id, publication_date, isbn, book_type, page_count))
                    book_id = cur.fetchone()[0]
                    # add publisher relationships if found

                    try:
                        position = 1
                        for publisher in book['publishers']:
                            if len(publisher) > 250:
                                # log this latter
                                print_log_entry(error_log,"This book's publisher (%s) is too long, not importing it for the moment! Continuing..." % publisher)
                                continue
                            print_log_entry(log_file,"Checking to see if a publisher entry exists for %s..." % publisher)
                            cur.execute('''
                                SELECT publicist_id
                                FROM publicist
                                WHERE publicist_name = %s
                            ''', (publisher,))

                            if cur.rowcount != 1:
                                print_log_entry(log_file,"No publisher entry found, adding one now(%s)..." % loop_counter)
                                print_log_entry(log_file,"Inserting publisher: %s :: %s." % (publisher, loop_counter))
                                cur.execute('''
                                  INSERT INTO publicist (publicist_name)
                                  VALUES(%s)
                                  RETURNING publicist_id
                                ''', (publisher,))

                            publicist_id = cur.fetchone()[0]
                            cur.execute('''
                              INSERT INTO book_publication (book_id, publicist_id, position)
                              VALUES(%s, %s,%s)
                            ''', (book_id,publicist_id,position))
                            position += 1
                    except KeyError:
                        print_log_entry(error_log,"KeyError importing publisher(s) for (%s)!" % loop_counter)

                try:
                    for subject in book['subjects']:
                        subject = subject.strip().encode('ascii', 'xmlcharrefreplace')
                        #print "Checking to see if a subject entry exists for %s..." % tag
                        cur.execute('''
                            SELECT subject_id
                            FROM subject_genre
                            WHERE subject_name = %s
                        ''', (subject,))

                        if cur.rowcount != 1:
                            print_log_entry(log_file,"No subject entry found, adding one now(%s)..." % loop_counter)
                            #too many, or no, matching book_core entries found -> make a new one
                            print_log_entry(log_file,"Inserting subject: %s :: %s." % (subject, loop_counter))
                            cur.execute('''
                              INSERT INTO subject_genre (subject_name)
                              VALUES(%s)
                              RETURNING subject_id
                            ''', (subject,))

                        # Retrieve book_core_id for book insertion
                        subject_id = cur.fetchone()[0]

                        cur.execute('''
                          INSERT INTO book_categorization (core_id, subject_id)
                          VALUES(%s, %s)
                        ''', (book_core_id,subject_id))
                except KeyError:
                    print_log_entry(error_log,"Unable to access book['subjects'] for tag creation (%s)..." % loop_counter)


                # add author relationships if found
                position = 1
                try:
                    for author in book['authors']:
                        position += 1
                        try:
                            author_id = author_ids[author]
                            cur.execute('''
                            INSERT INTO authorship (core_id, author_id, position)
                            VALUES(%s, %s, %s)
                            RETURNING author_id
                            ''', (book_core_id, author_id, position))
                            position += 1
                        except KeyError:
                            print_log_entry(error_log,"KeyError: Couldn't find an author_id entry for author key: %s..." % author)
                        except TypeError:
                            print_log_entry(error_log,"TypeError: Couldn't find an author_id entry for author key: %s..." % author)
                except KeyError:
                    print_log_entry(error_log,"No authors found!")
except:
    e = sys.exc_info()[0]
    traceback.print_exc(file=sys.stdout)
    print_log_entry(error_log,"Big time error! %s" % e)


sorted_author_keys = sorted(author_keys.items(), key=operator.itemgetter(1), reverse=True)
sorted_work_keys = sorted(work_keys.items(), key=operator.itemgetter(1), reverse=True)
sorted_book_keys = sorted(book_keys.items(), key=operator.itemgetter(1), reverse=True)

markdown_file = open('load-template-results.md', 'w')
print_key_occurrences("Author Keys", markdown_file, sorted_author_keys)
print_key_occurrences("Work Keys", markdown_file, sorted_work_keys)
print_key_occurrences("Book Keys", markdown_file, sorted_book_keys)

markdown_file.close()
log_file.close()
error_log.close()
