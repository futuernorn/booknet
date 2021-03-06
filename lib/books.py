"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

from psycopg2 import errorcodes

BOOKS_PER_PAGE = 15;

QUERIES = {
    'books_count': '''
        SELECT COUNT(*) FROM book_core JOIN book USING (core_id);
    ''',
    'books_with_covers_count': '''
        SELECT COUNT(*) FROM book_core JOIN book USING (core_id) WHERE cover_name IS NOT NULL;
    ''',
    'books_by_subjects_count': '''
        SELECT COUNT(*) FROM subject_genre;
    ''',
    'books_by_subject_count': '''
        SELECT COUNT(*) FROM subject_genre WHERE subject_id = %s
    ''',
    'books_by_authors_count': '''
        SELECT COUNT(*) FROM author;
    ''',
    'books_by_publishers_count': '''
        SELECT COUNT(*) FROM author;
    ''',
    'books_search_count': '''
        SELECT COUNT(DISTINCT book_id)
        FROM book
        JOIN book_search USING (book_id)
        WHERE search_vector @@ plainto_tsquery('%s')
    ''',
    'books_by_subjects': '''
        SELECT subject_id, subject_name, AVG(rating) as avg_rating, COUNT(DISTINCT core_id) as num_books, SUM(page_count) as num_pages
        FROM subject
        JOIN book_subject USING (subject_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN book USING (core_id)
        %s
        GROUP BY subject_id, subject_name
        %s
        LIMIT %s OFFSET %s
    ''',
    'books_by_authors': '''
        SELECT author_id, author_name, AVG(rating) as avg_rating, COUNT(DISTINCT core_id) as num_books, SUM(page_count) as num_pages
        FROM author
        JOIN book_author USING (author_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN book USING (core_id)
        %s
        GROUP BY author_id, author_name
        %s
        LIMIT %s OFFSET %s
    ''',
    'books_by_publishers': '''
        SELECT publisher_id, publisher_name, AVG(rating) as avg_rating, COUNT(DISTINCT core_id) as num_books, SUM(page_count) as num_pages
        FROM publisher
        JOIN book_publisher USING (publisher_id)
        LEFT JOIN ratings USING (book_id)
        LEFT JOIN book USING (book_id)
        %s
        GROUP BY publisher_id, publisher_name
        %s
        LIMIT %s OFFSET %s
    ''',
    'select_books': '''
        SELECT core_id, book_title, book_description, isbn, page_count, cover_name,
          AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers
        FROM book_core
        JOIN book USING (core_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN user_log ON core_id = user_log.book_id
        WHERE book.is_active = TRUE
        GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date
        %s
        LIMIT %s OFFSET %s
    ''',
    'select_books_where': '''
        SELECT core_id, book_title, book_description, isbn, COALESCE(page_count,0), COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers
        FROM book_core
        LEFT JOIN book USING (core_id)
        %s
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN user_log ON core_id = user_log.book_id
        LEFT JOIN book_subject USING (core_id)
        WHERE book.is_active = TRUE %s
        GROUP BY %s core_id, book_title, book_description, cover_name, isbn, page_count, publication_date
        %s
        %s
    ''',
    'select_book_info': '''
        SELECT %s
        FROM %s JOIN %s USING (%s)
        WHERE core_id = %s
    ''',
    'select_book_title': '''
        SELECT core_id, book_title
        FROM book_core
        JOIN book USING (core_id)
        WHERE core_id = %s;
    '''
}

SORTING = {
    'book_title': 'ORDER BY book_title',
    'publication_date': 'ORDER BY publication_date',
    'num_reader': 'ORDER BY num_reader',
    'num_books': 'ORDER BY num_books',
    'num_pages': 'ORDER BY num_pages',
    'subject_name': 'ORDER BY subject_name',
    'average_rating': 'ORDER BY avg_rating'
}

SORT_DIRECTION = {
    'ASC': 'ASC',
    'DESC': 'DESC'
}

def get_total_pages(cur, query):
    cur.execute(query)
    total_books = cur.fetchone()[0];
    total_pages = (total_books / BOOKS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_books(cur, amount):
    return get_books(cur, 0, amount)

def generate_book_info(cur, current_user_id):
    '''
    Common function used on any page that needs to generate a 'book_index'; table of books with common info / actions.
    :param cur:
    :param current_user_id:
    :return: book_info, array of dicts containing all need infor on a given book
    '''
    book_info = []
    for core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        discrete_rating = generate_discrete_rating(discrete_rating)
        avg_rating = format_rating(avg_rating)

        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        query = QUERIES['select_book_info'] % ('author_name', 'author', 'book_author', 'author_id', '%s')
        cur.execute(query, (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        cur.execute('''
        SELECT subject_name
        FROM subject JOIN book_subject USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        if (current_user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], current_user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]

    return book_info

def get_books(cur, start, amount, current_user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    total_pages = get_total_pages(cur, QUERIES['books_count'])
    cur.execute(QUERIES['select_books'] % (order_by,'%s','%s'), (amount, start))

    book_info = generate_book_info(cur, current_user_id)

    return total_pages, book_info

def get_book(cur, book_id, current_user_id=None):
    '''
    Data for just one book, used for a single-item book page
    :param cur:
    :param book_id:
    :param current_user_id:
    :return:
    '''
    cur.execute('''
        SELECT DISTINCT core_id,book_title, isbn, page_count, COALESCE(publisher_name,'Unknown'), book_description,
        to_char(publication_date,'Mon. DD, YYYY') as publication_date, to_char(publication_date,'MM/DD/YYYY') as publication_date_fmt,
        COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating
        FROM book_core
        LEFT JOIN book USING (core_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN book_publisher ON core_id = book_publisher.book_id
        LEFT JOIN publisher USING (publisher_id)
        WHERE core_id = %s
        GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date, publication_date_fmt, publisher_name
    ''', (book_id,))

    book_info = {'core_id': book_id, 'title': 'Error loading data...'}

    for core_id, book_title, isbn, page_count, publisher_name, book_description, publication_date, publication_date_fmt, cover_name, avg_rating in cur:
        discrete_rating = generate_discrete_rating(avg_rating)
        avg_rating = format_rating(avg_rating)
        book_info = {'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'), 'isbn': isbn,
                     'num_pages': page_count, 'publisher_name': publisher_name.decode('utf8', 'xmlcharrefreplace'), 'cover_name': cover_name, 'authors': [],
                     'subjects': [], 'avg_rating': avg_rating, 'book_description': book_description.decode('utf8', 'xmlcharrefreplace'),
                     'publication_date': publication_date, 'publication_date_fmt': publication_date_fmt, 'containing_lists': [], 'reading_logs': [], 'reviews': [],
                     'discrete_rating': discrete_rating}

    # Get authors
    cur.execute('''
    SELECT author_name
    FROM author JOIN book_author USING (author_id)
    WHERE core_id = %s
    ''', (book_info['core_id'],))

    author_info = []
    for author_name in cur:
        author_info.append(author_name[0].decode('utf8', 'xmlcharrefreplace'))
    book_info['authors'] = author_info
    book_info['author_count'] = cur.rowcount

    # Get subjects
    cur.execute('''
    SELECT subject_name
    FROM subject JOIN book_subject USING (subject_id)
    WHERE core_id = %s
    ''', (book_info['core_id'],))

    book_info['subjects_count'] = cur.rowcount
    subject_info = []
    for subject_name in cur:
        subject_info.append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
    book_info['subjects'] = subject_info

    # Get associated lists
    # First get list_id's
    associated_lists = []
    cur.execute('''
        SELECT list_id
        FROM list
        JOIN book_list USING (list_id)
        WHERE book_id = %s
        ''', (book_info['core_id'],))
    for list_id in cur:
        associated_lists.append(list_id[0])

    for list_id in associated_lists:
        cur.execute('''
        SELECT list_name, user_id, login_name, to_char(list.date_created,'Mon. DD, YYYY') as date_created, COUNT(DISTINCT book_id) as num_books
        FROM list
        JOIN book_list USING (list_id)
        JOIN booknet_user USING (user_id)
        WHERE list_id = %s
        GROUP BY list_id, list_name, user_id, login_name, list.date_created
        ''', (list_id,))

        for list_name, user_id, login_name, date_created, num_books in cur:
            book_info['containing_lists'].append({'id': list_id, 'list_name': list_name, 'user_id': user_id,
                                                  'login_name': login_name, 'date_created': date_created, 'num_books': num_books})


    # Get logs
    cur.execute('''
        SELECT log_id, user_id, login_name, log_text, to_char(date_started,'Mon. DD, YYYY') as date_started,
          to_char(date_completed,'Mon. DD, YYYY') as date_completed
        FROM user_log
        JOIN book_core ON book_id = core_id
        JOIN booknet_user ON user_id = reader
        WHERE core_id = %s
    ''', (book_id,))
    for log_id, user_id, login_name, log_text, date_started, date_completed in cur:
        try:
            book_info['reading_logs'].append({'log_id': log_id, 'user_id': user_id, 'login_name': login_name,
                                              'log_text': log_text, 'date_started': date_started, 'date_completed': date_completed})
        except KeyError:
                print "Missing book_info for book_id %s?" % book_id

    # Get reviews
    cur.execute('''
        SELECT review_id, user_id, login_name, to_char(date_reviewed,'Mon. DD, YYYY') as date_reviewed, review_text
        FROM review
        JOIN book_core ON book_id = core_id
        JOIN booknet_user ON user_id = reviewer
        WHERE core_id = %s
    ''', (book_id,))
    for review_id, user_id, login_name, date_reviewed, review_text in cur:
        book_info['reviews'].append({'review_id': review_id, 'user_id': user_id, 'date_reviewed': date_reviewed,
                                'review_text': review_text, 'login_name': login_name})
    if (current_user_id):
        cur.execute('''
        SELECT rating
        FROM ratings
        WHERE book_id = %s AND rater = %s
        ''', (book_info['core_id'], current_user_id))
        if cur.rowcount > 0:
            book_info['user_rating'] = cur.fetchone()[0]
    return book_info

def get_book_title(cur, book_id):
    cur.execute(QUERIES['select_book_title'], (book_id,))

    for core_id, book_title in cur:
        return book_title.decode('utf8', 'xmlcharrefreplace'), core_id

def get_books_with_covers(cur, start, amount, current_user_id=None, sorting=None, sort_direction=None):
    '''
    Silly "easter egg" function include just to view more complete views that would be possible with further work/data.
    :param cur:
    :param start:
    :param amount:
    :param user_id:
    :param sorting:
    :param sort_direction:
    :return:
    '''

    order_by = generate_sorting(sorting, sort_direction)


    total_pages = get_total_pages(cur, QUERIES['books_with_covers_count'])
    cur.execute(QUERIES['select_books'] % (order_by,'%s','%s'), (amount, start))
    query = QUERIES['select_books_where'] % ('', '', ' AND cover_name IS NOT NULL', '', order_by,'LIMIT %s OFFSET %s')
    cur.execute(query, (amount, start))


    book_info = generate_book_info(cur, current_user_id)

    return total_pages, book_info

########################## Publishers #####################################################################################
def get_books_by_publishers(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    total_pages = get_total_pages(cur, QUERIES['books_by_publishers_count'])
    query = QUERIES['books_by_publishers'] % ('', order_by,'%s','%s')
    cur.execute(query, (amount, start))

    publisher_info = []
    for publisher_id, publisher_name, avg_rating, num_books, num_pages in cur:
        try:
            avg_rating = round(avg_rating,2)
        except TypeError:
            # not a float / null
            pass
        print avg_rating
        publisher_info.append({'id':publisher_id, 'name': publisher_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})

    return total_pages, publisher_info

def get_books_by_publisher(cur, start, amount, publisher_id, current_user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    query = QUERIES['select_books_where'] % ('JOIN book_publisher ON core_id = book_publisher.book_id',
                                                 ' AND publisher_id = %s', 'publisher_id,', order_by,'LIMIT %s OFFSET %s')
    cur.execute(query, (publisher_id, amount, start))


    total_books = cur.rowcount
    total_pages = int((total_books / BOOKS_PER_PAGE) + 1);

    book_info = generate_book_info(cur, current_user_id)

    cur.execute(QUERIES['books_by_publishers'] % ('WHERE publisher_id = %s', order_by,'%s','%s'), (publisher_id, amount, start))


    for publisher_id, publisher_name, avg_rating, num_books, num_pages in cur:
        publisher_info = {'id':publisher_id, 'name': publisher_name.decode('utf8', 'xmlcharrefreplace'), 'books': book_info,
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages}

    return total_pages, publisher_info


########################## Authors #####################################################################################
def get_books_by_authors(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    total_pages = get_total_pages(cur, QUERIES['books_by_authors_count'])
    cur.execute(QUERIES['books_by_authors'] % ('', order_by,'%s','%s'), (amount, start))

    author_info = []
    for author_id, author_name, avg_rating, num_books, num_pages in cur:
        avg_rating = format_rating(avg_rating)

        author_info.append({'id':author_id, 'name': author_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})

    return total_pages, author_info


def get_books_by_author(cur, start, amount, author_name, current_user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    cur.execute('''
        SELECT author_id
        FROM author
        WHERE author_name = %s
    ''', (author_name,))
    author_id = cur.fetchone()[0]
    query = QUERIES['select_books_where'] % ('JOIN authorship USING(core_id)',
                                             ' AND author_id = %s', 'author_id,', order_by,'LIMIT %s OFFSET %s')
    cur.execute(query, (author_id, amount, start))


    total_books = cur.rowcount
    total_pages = int((total_books / BOOKS_PER_PAGE) + 1);

    book_info = generate_book_info(cur, current_user_id)

    cur.execute(QUERIES['books_by_authors'] % ('WHERE author_id = %s', order_by,'%s','%s'), (author_id, amount, start))


    for author_id, author_name, avg_rating, num_books, num_pages in cur:
        author_info = {'id':author_id, 'name': author_name.decode('utf8', 'xmlcharrefreplace'), 'books': book_info,
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages}

    return total_pages, author_info


############################## Subjects ################################################################################
def get_books_by_subjects(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    order_by = generate_sorting(sorting, sort_direction)

    total_pages = get_total_pages(cur, QUERIES['books_by_subjects_count'])
    query = QUERIES['books_by_subjects'] % ('', order_by,'%s','%s')
    cur.execute(query, (amount, start))



    book_info = []
    for subject_id, subject_name, avg_rating, num_books, num_pages in cur:
        avg_rating = format_rating(avg_rating)
        book_info.append({'id':subject_id, 'subject': subject_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})


    return total_pages, book_info


def get_books_by_subject(cur, start, amount, subject, current_user_id=None, sorting=None, sort_direction=None):

    order_by = generate_sorting(sorting, sort_direction)

    cur.execute('''
        SELECT subject_id
        FROM subject_genre
        WHERE subject_name = %s
    ''', (subject,))
    subject_id = cur.fetchone()[0]

    total_pages = get_total_pages(cur, QUERIES['books_by_subject_count'] % subject_id)

    query = QUERIES['select_books_where'] % ('', ' AND subject_id = %s',
                                             'subject_id,', order_by, 'LIMIT %s OFFSET %s')

    cur.execute(query, (subject_id, amount, start))

    book_info = generate_book_info(cur, current_user_id)

    return total_pages, book_info


########################## Lists #######################################################################################

def get_books_in_list(cur, lid, current_user_id=None):
    query = QUERIES['select_books_where'] % ('JOIN book_list ON core_id = book_list.book_id', ' AND list_id = %s',
                                             'list_id,', '', '')

    cur.execute(query, (lid,))

    book_info = generate_book_info(cur, current_user_id)

    return book_info

#################### Utility ###########################################################################################
def search_books(cur, search_query, start,amount, current_user_id=None, sorting=None, sort_direction=None):
    order_by = 'ORDER BY ts_rank(search_vector, plainto_tsquery(\'%s\')) DESC'
    try:
        order_by += ', '+SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        pass

    total_pages = get_total_pages(cur, QUERIES['books_search_count'] % search_query)

    query = QUERIES['select_books_where'] % ('', 'JOIN book_search USING (book_id)',' AND search_vector @@ plainto_tsquery(\'%s\')',
                                             'search_vector,', order_by,'LIMIT %s OFFSET %s')

    cur.execute(query % (search_query, search_query,'%s','%s'), (amount, start))



    book_info = generate_book_info(cur, current_user_id)

    return total_pages, book_info

#################### Modifications #####################################################################################

# Ratings ########################
def add_rating(cur, book_id, rating, user_id):
    status = True
    message = []
    book_info = get_book(cur, book_id)

    cur.execute('''
        SELECT ratings
        FROM ratings
        WHERE book_id = %s AND rater = %s
    ''', (book_id, user_id))

    if cur.rowcount == 1:
        cur.execute('''
          UPDATE ratings SET rating = %s
          WHERE book_id = %s AND rater = %s
          RETURNING ratings
        ''', (rating, book_info['core_id'], user_id))
        if cur.rowcount == 1:
            message.append("Rating of %s updated for %s!" % (rating, book_info['title']))
        else:
            message.append("Unknown error!")
            status = False

    else:
        cur.execute('''
          INSERT INTO ratings (book_id, rater, rating, date_rated)
          VALUES(%s, %s, %s, current_timestamp)
          RETURNING ratings
        ''', (book_info['core_id'], user_id, rating))
        if cur.rowcount == 1:
            message.append("Rating of %s saved for %s!" % (rating, book_info['title']))
        else:
            message.append("Unknown error!")
            status = False

    return status, message

def remove_rating(cur, book_id, user_id):
    status = True
    message = []
    book_info = get_book(cur, book_id)

    cur.execute('''
        DELETE FROM ratings
        WHERE book_id = %s AND rater = %s
    ''', (book_id, user_id))

    if cur.rowcount == 1:
        message.append("Rating removed for %s!" % (book_info['title']))
    else:
        message.append("Unknown error!")
        status = False

    return status, message

# Add / edit ###############################################
def edit_book(cur, book_id, form):
    update_status = True
    message = []
    author_names = {}
    subjects = []
    for key, value in form.iteritems():
        if 'inputBookAuthor' in key:
            author_names[key[15:]] = value #try to keep position
        if 'inputBookSubject' in key:
            subjects.append(value)
            
    publication_date = form['inputBookPubDate']
    isbn = form['inputBookISBN']
    page_count = form['inputBookPageCount']
    book_type = form['inputBookType']
    book_title = form['inputBookTitle']
    book_description = form['inputBookDescription']
    
    cur.execute('''
        UPDATE book SET
        publication_date = %s
        ISBN = %s
        book_type = %s
        page_count = %s
        book_title = %s
        WHERE book_id = %s
        RETURNING book_id
    ''', (publication_date, isbn, book_type, page_count, book_title, book_id))
    if cur.rowcount == 1:
        message.append("Book %s updated!" % book_title)

    else:
        message.append("Unknown error!")
        status = False

    for position,author in author_names.iteritems():
        # First check to see if we have a matching author
        cur.execute('''
        SELECT author_id
        FROM author
        WHERE author_name = %s
        ''', (author,))
        if cur.rowcount == 0:
            # Need to insert this author
            cur.execute('''
            INSERT INTO author (author_name)
            VALUES(%s)
            RETURNING author_id
            ''', (author,))
        author_id = cur.fetchone()[0]

        # Now we see if this author is already associated with our book
        cur.execute('''
        SELECT authorship_id
        FROM authorship
        WHERE core_id = %s AND author_id = %s
        ''', (book_id,author))
        if cur.rowcount == 0:
            # Need to insert this author
            cur.execute('''
            INSERT INTO authorship (core_id, author_id, position)
            VALUES(%s, %s, %s)
            RETURNING authorship_id
            ''', (book_id,author_id,position))
        authorship_id = cur.fetchone()[0]
     
    for subject in subjects:
        
        cur.execute('''
        SELECT subject_id
        FROM subject_genre
        WHERE subject_name = %s
        ''', (subject,))
        if cur.rowcount == 0:
            # Need to insert this subject
            cur.execute('''
            INSERT INTO subject_genre (subject)
            VALUES(%s)
            RETURNING subject_id
            ''', (subject,))
        subject_id = cur.fetchone()[0]

        # Now we see if this author is already associated with our book
        cur.execute('''
        SELECT categorize_id
        FROM book_categorization
        WHERE core_id = %s AND subject_id = %s
        ''', (book_id,subject))
        if cur.rowcount == 0:            
            cur.execute('''
            INSERT INTO book_categorization (core_id, subject_id)
            VALUES(%s, %s)
            RETURNING authorship_id
            ''', (book_id,author_id))
        categorize_id = cur.fetchone()[0]

    return update_status, message

def add_book(cur, core_id, user_id, form):
    update_status = True
    message = []
    author_names = {}
    subjects = []
    for key, value in form.iteritems():
        if 'inputBookAuthor' in key:
            author_names[key[15:]] = value #try to keep position
        if 'inputBookSubject' in key:
            subjects.append(value)

    publication_date = form['inputBookPubDate']
    isbn = form['inputBookISBN']
    page_count = form['inputBookPageCount']
    book_type = form['inputBookType']
    book_title = form['inputBookTitle']
    book_description = form['inputBookDescription']
    request_text = form['inputBookRequestText']

    print "Data parsed..."
    # Do we have a book_core to match? [Obviously needs a more robust solution.]
    if core_id == 0:
        cur.execute('''
            SELECT core_id
            FROM book_core
            WHERE book_title = %s
        ''', (book_title,))
        if cur.rowcount < 1:
            cur.execute('''
              INSERT INTO book_core (book_title, book_description, edition, is_active)
              VALUES(%s, %s, %s, %s)
              RETURNING core_id
            ''', (book_title, book_description, 1, False))
        core_id = cur.fetchone()[0]

    cur.execute('''
        INSERT INTO book (core_id, publication_date, isbn, book_type, page_count, is_active)
        VALUES(%s, %s, %s, %s, %s, %s)
        RETURNING book_id
    ''', (core_id, publication_date, isbn, book_type, page_count, False))

    if cur.rowcount > 0:
        book_id = cur.fetchone()[0]
        message.append("New book %s queued for insertion!" % book_title)

    else:
        message.append("Unknown error!")
        return False, message, 0

    for position,author in author_names.iteritems():
        # First check to see if we have a matching author
        cur.execute('''
        SELECT author_id
        FROM author
        WHERE author_name = %s
        ''', (author,))
        if cur.rowcount == 0:
            # Need to insert this author
            cur.execute('''
            INSERT INTO author (author_name)
            VALUES(%s)
            RETURNING author_id
            ''', (author,))
        author_id = cur.fetchone()[0]

        # Now we see if this author is already associated with our book
        cur.execute('''
        SELECT authorship_id
        FROM authorship
        JOIN author USING (author_id)
        WHERE core_id = %s AND author_name = %s
        ''', (core_id,author))
        if cur.rowcount == 0:
            # Need to insert this author
            cur.execute('''
            INSERT INTO authorship (core_id, author_id, position)
            VALUES(%s, %s, %s)
            RETURNING authorship_id
            ''', (core_id,author_id,position))
        authorship_id = cur.fetchone()[0]

    for subject in subjects:

        cur.execute('''
        SELECT subject_id
        FROM subject_genre
        WHERE subject_name = %s
        ''', (subject,))
        if cur.rowcount == 0:
            # Need to insert this subject
            cur.execute('''
            INSERT INTO subject_genre (subject_name)
            VALUES(%s)
            RETURNING subject_id
            ''', (subject,))
        subject_id = cur.fetchone()[0]

        # Now we see if this author is already associated with our book
        cur.execute('''
        SELECT categorize_id
        FROM book_categorization
        JOIN subject_genre USING (subject_id)
        WHERE core_id = %s AND subject_name = %s
        ''', (core_id,subject))
        if cur.rowcount == 0:
            cur.execute('''
            INSERT INTO book_categorization (core_id, subject_id)
            VALUES(%s, %s)
            RETURNING categorize_id
            ''', (core_id,subject_id))
        categorize_id = cur.fetchone()[0]

    # Recreate book_search  information
    cur.execute('''
        TRUNCATE TABLE book_search;
        INSERT INTO book_search (book_id, search_vector)
            SELECT book_id,
            setweight(to_tsvector(book_title), 'A')
            || setweight(to_tsvector(coalesce(book_description, '')), 'B')
            FROM books
            LEFT OUTER JOIN (SELECT core_id, book_title, book_description
                             FROM book_core) core_info
        USING (core_id);
    ''')

    cur.execute("ANALYZE;")

    # And finally enter the new book in the queue for approval
    cur.execute('''
        INSERT INTO request (user_id, type, date_requested, priority, status, date_of_status)
        VALUES(%s, %s, NOW(), %s, %s, NOW())
        RETURNING request_id
    ''', (user_id, "Add Book", '1', "Awaiting Review"))
    request_id = cur.fetchone()[0]

    cur.execute('''
        INSERT INTO request_on_book (request_id, book_id, request_type, request_text)
        VALUES(%s, %s, %s, %s)
        RETURNING request_on_book_id
    ''', (request_id, book_id, "Add Book", request_text))

    return True, message, core_id

def set_book_active(cur,book_id):
    update_status = True
    message = []
    core_id = 0

    cur.execute('''
        SELECT core_id
        FROM book
        JOIN book_core USING (core_id)
	    WHERE book_id = %s
    ''', (book_id,))
    core_id = cur.fetchone()[0]

    book_title = get_book_title(cur, core_id)

    cur.execute('''
        UPDATE book SET
        is_active = TRUE
        WHERE book_id = %s
        RETURNING book_id
    ''', (book_id,))
    if cur.rowcount == 1:
        message.append("Book %s activated!" % book_title)

    else:
        message.append("Unknown error!")

    cur.execute('''
        UPDATE book_core SET
        is_active = TRUE
        WHERE core_id = %s
        RETURNING core_id
    ''', (core_id,))
    if cur.rowcount == 1:
        message.append("Book core id %s activated!" % core_id)

    else:
        message.append("Unknown error!")

    return update_status, message, core_id

def add_log(cur, user_id, form):
    create_status = True
    message = []
    log_id = 0

    book_id = form['book_id']
    book_title, book_core = get_book_title(cur, book_id);
    log_text = form['log_input']
    date_started = form['starting_date']
    date_completed = form['date_completed']
    pages_read = form['pages_read']
    current_status = form['current_status =']

    cur.execute('''
      INSERT INTO user_log (book_id, reader, status, date_completed, pages_read, log_text, date_started)
      VALUES(%s, %s, %s, %s, %s %s, %s)
      RETURNING log_id
    ''', (book_id, user_id, current_status, date_completed, pages_read, log_text, date_started))
    if cur.rowcount == 1:
        log_id = cur.fetchone()[0]
        message.append("Created new log for: %s!" % book_title)
    else:
        message.append("Unknown error!")
        create_status = False

    return create_status, message, log_id

# def delete_list(cur,list_id,user_id):


############################### Utility #########################
def format_rating(avg_rating):
    try:
        return round(avg_rating,2)
    except TypeError:
        # not a float / null
        pass
    return avg_rating


def generate_discrete_rating(avg_rating):
    if avg_rating:
        discrete_rating = round(avg_rating*2) / 2
    else:
        discrete_rating = 0
    return discrete_rating

def generate_sorting(sorting, sort_direction):
    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided
    return order_by