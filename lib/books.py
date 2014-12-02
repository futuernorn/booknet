"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

from psycopg2 import errorcodes

BOOKS_PER_PAGE = 15;

QUERIES = {
    'books_count': '''
        SELECT COUNT(*) FROM book_core;
    ''',
    'books_by_subjects_count': '''
        SELECT COUNT(*) FROM subject_genre;
    ''',
    'books_by_authors_count': '''
        SELECT COUNT(*) FROM author;
    ''',
    'books_by_publishers_count': '''
        SELECT COUNT(*) FROM author;
    ''',
    'books_by_subjects': '''
        SELECT subject_id, subject_name, AVG(rating) as avg_rating, COUNT(DISTINCT core_id) as num_books, SUM(page_count) as num_pages
        FROM subject_genre
        JOIN book_categorization USING (subject_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN books USING (core_id)
        GROUP BY subject_id, subject_name
        %s
        LIMIT %s OFFSET %s
    ''',
    'books_by_authors': '''
        SELECT author_id, author_name, AVG(rating) as avg_rating, COUNT(DISTINCT core_id) as num_books, SUM(page_count) as num_pages
        FROM author
        JOIN authorship USING (author_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN books USING (core_id)
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
        LEFT JOIN books USING (book_id)
        %s
        GROUP BY publisher_id, publisher_name
        %s
        LIMIT %s OFFSET %s
    ''',
    'select_books': '''
        SELECT core_id, book_title, book_description, isbn, page_count, COALESCE(cover_name,'_placeholder') as cover_name,
          AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers
        FROM book_core
        JOIN books USING (core_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        JOIN user_log ON core_id = user_log.book_id
        GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date
        %s
        LIMIT %s OFFSET %s
    ''',
    'select_books_where': '''
        SELECT %s, core_id, book_title, book_description, isbn, page_count, COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers
        FROM book_core
        LEFT JOIN books USING (core_id)
        %s
        LEFT JOIN ratings ON core_id = ratings.book_id
        LEFT JOIN user_log ON core_id = user_log.book_id
        LEFT JOIN book_categorization USING (core_id)
        %s
        GROUP BY %s, core_id, book_title, book_description, cover_name, isbn, page_count, publication_date
        %s
        LIMIT %s OFFSET %s
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

def get_total_pages(cur,query):
    cur.execute(query)
    total_books = cur.fetchone()[0];
    total_pages = (total_books / BOOKS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_books(cur, amount):
    return get_book_range(cur,0,amount)

def get_all_books(cur, page, user_id, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_book_range(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, user_id,  sorting, sort_direction)

def get_book_range(cur,start,amount, user_id=None, sorting=None, sort_direction=None):
    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = ''

    total_pages = get_total_pages(cur, QUERIES['books_count'])
    cur.execute(QUERIES['select_books'] % (order_by,'%s','%s'), (amount, start))



    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if not cover_name:
            cover_name = '_placeholder'
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        # print book['authors']
        cur.execute('''
        SELECT subject_name
        FROM subject_genre JOIN book_categorization USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        # subject_info = []
        # print cur.fetchone()
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        # book['subjects'] = subject_info
        if (user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]
        # print book['subjects']


    return total_pages, book_info

def get_all_books_by_publishers(cur, page, user_id, sorting, sort_direction):
    return get_books_by_publishers(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, user_id,  sorting, sort_direction)


def get_books_by_publishers(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    # sanitize inputs(?)
    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided

    total_pages = get_total_pages(cur, QUERIES['books_by_publishers_count'])
    cur.execute(QUERIES['books_by_publishers'] % (order_by,'%s','%s'), (amount, start))

    publisher_info = []
    for publisher_id, publisher_name, avg_rating, num_books, num_pages in cur:
        publisher_info.append({'id':publisher_id, 'name': publisher_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})

    return total_pages, publisher_info

def get_all_books_by_authors(cur, page, user_id, sorting, sort_direction):
    return get_books_by_authors(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, user_id,  sorting, sort_direction)


def get_books_by_authors(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    # sanitize inputs(?)
    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided

    total_pages = get_total_pages(cur, QUERIES['books_by_authors_count'])
    cur.execute(QUERIES['books_by_authors'] % ('', order_by,'%s','%s'), (amount, start))

    author_info = []
    for author_id, author_name, avg_rating, num_books, num_pages in cur:
        print author_name
        author_info.append({'id':author_id, 'name': author_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})

    return total_pages, author_info

def get_all_books_by_author(cur, page, author_name, user_id, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_books_by_author(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, author_name, user_id,  sorting, sort_direction)


def get_books_by_author(cur, start, amount, author_name, user_id=None, sorting=None, sort_direction=None):

    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided

    cur.execute('''
        SELECT author_id
        FROM author
        WHERE author_name = %s
    ''', (author_name,))
    author_id = cur.fetchone()[0]

    cur.execute(QUERIES['select_books_where'] % ('WHERE author_id = %s', order_by,'%s','%s'), (author_id, amount, start))


    total_books = cur.rowcount
    total_pages = int((total_books / BOOKS_PER_PAGE) + 1);

    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for author_id, core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        # print book['authors']
        cur.execute('''
        SELECT subject_name
        FROM subject_genre JOIN book_categorization USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        # subject_info = []
        # print cur.fetchone()
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        # book['subjects'] = subject_info
        if (user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]
        # print book['subjects']

    cur.execute(QUERIES['books_by_authors'] % ('WHERE author_id = %s', order_by,'%s','%s'), (author_id, amount, start))


    for author_id, author_name, avg_rating, num_books, num_pages in cur:
        print author_name
        author_info = {'id':author_id, 'name': author_name.decode('utf8', 'xmlcharrefreplace'), 'books': book_info,
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages}

    return total_pages, author_info

def get_all_books_by_publisher(cur, page, publisher_id, user_id, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_books_by_publisher(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, publisher_id, user_id,  sorting, sort_direction)


def get_books_by_publisher(cur, start, amount, publisher_id, user_id=None, sorting=None, sort_direction=None):

    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided

    # cur.execute('''
    #     SELECT author_id
    #     FROM author
    #     WHERE author_name = %s
    # ''', (author_name,))
    # author_id = cur.fetchone()[0]

    cur.execute(QUERIES['select_books_where'] % ('publisher_id', 'JOIN book_publisher ON core_id = book_publisher.book_id', 'WHERE publisher_id = %s', 'publisher_id', order_by,'%s','%s'), (publisher_id, amount, start))


    total_books = cur.rowcount
    total_pages = int((total_books / BOOKS_PER_PAGE) + 1);

    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for author_id, core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        # print book['authors']
        cur.execute('''
        SELECT subject_name
        FROM subject_genre JOIN book_categorization USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        # subject_info = []
        # print cur.fetchone()
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        # book['subjects'] = subject_info
        if (user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]
        # print book['subjects']

    cur.execute(QUERIES['books_by_publishers'] % ('WHERE publisher_id = %s', order_by,'%s','%s'), (publisher_id, amount, start))


    for publisher_id, publisher_name, avg_rating, num_books, num_pages in cur:
        publisher_info = {'id':publisher_id, 'name': publisher_name.decode('utf8', 'xmlcharrefreplace'), 'books': book_info,
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages}

    return total_pages, publisher_info


def get_all_books_by_subjects(cur, page, user_id, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_books_by_subjects(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, user_id,  sorting, sort_direction)


def get_books_by_subjects(cur, start, amount, user_id=None, sorting=None, sort_direction=None):
    # sanitize inputs(?)
    try:
        order_by = SORTING[sorting]+' '+SORT_DIRECTION[sort_direction]
    except KeyError:
        order_by = '' #no sorting requested or inproper parameters provided

    total_pages = get_total_pages(cur, QUERIES['books_by_subjects_count'])
    cur.execute(QUERIES['books_by_subjects'] % (order_by,'%s','%s'), (amount, start))



    book_info = []
    for subject_id, subject_name, avg_rating, num_books, num_pages in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'id':subject_id, 'subject': subject_name.decode('utf8', 'xmlcharrefreplace'),
                          'avg_rating': avg_rating, 'num_books': num_books, 'num_pages': num_pages})


    return total_pages, book_info

def get_all_books_by_subject(cur, page, subject, user_id, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_books_by_subject(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, subject, user_id,  sorting, sort_direction)


def get_books_by_subject (cur, start, amount, subject, user_id=None, sorting=None, sort_direction=None):

    if sorting and sort_direction:
        order_by = "ORDER BY %s %s " % (sorting,sort_direction) # this is stupid
    else:
        order_by = ""

    cur.execute('''
        SELECT subject_id
        FROM subject_genre
        WHERE subject_name = %s
    ''', (subject,))
    subject_id = cur.fetchone()[0]

    cur.execute(
        "SELECT core_id, book_title, book_description, isbn, page_count, COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers "+
        "FROM book_core "+
        "JOIN books USING (core_id) "+
        # "JOIN book_categorization USING (core_id) "+
        # "JOIN subject_genre USING (subject_id) "+
        "LEFT JOIN ratings ON core_id = ratings.book_id "+
        "JOIN user_log ON core_id = user_log.book_id "+
        "JOIN book_categorization USING (core_id) "
        # "GROUP BY core_id, book_id, picture, book_title, book_description, isbn, publication_date "+
        # order_by+
        # "SELECT DISTINCT core_id, book_title, book_description,  ROUND(AVG(rating)) as avg_rating "+
        # "FROM books "+
        # "JOIN book_core USING (core_id) "+
        # "JOIN book_categorization USING (core_id) "+
        # "JOIN subject_genre USING (subject_id) "+
        # "LEFT JOIN ratings USING (book_id) "+
        "WHERE subject_id = %s "
        "GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date " +
        order_by+
        "LIMIT %s OFFSET %s"
    , (subject_id, amount, start))


    total_books = cur.rowcount
    total_pages = int((total_books / BOOKS_PER_PAGE) + 1);

    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        # print book['authors']
        cur.execute('''
        SELECT subject_name
        FROM subject_genre JOIN book_categorization USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        # subject_info = []
        # print cur.fetchone()
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        # book['subjects'] = subject_info
        if (user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]
        # print book['subjects']


    return total_pages, book_info

def get_book(cur,book_id,user_id=None):
    cur.execute('''
        SELECT DISTINCT core_id,book_title, isbn, page_count, publisher_name, book_description,
        to_char(publication_date,'Mon. DD, YYYY') as publication_date, to_char(publication_date,'MM/DD/YYYY') as publication_date_fmt,
        COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating
        FROM book_core
        LEFT JOIN books USING (core_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        JOIN book_publisher ON core_id = book_publisher.book_id
        JOIN publisher USING (publisher_id)
        WHERE core_id = %s
        GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date, publication_date_fmt, publisher_name
    ''', (book_id,))
    book_info = {'core_id': book_id, 'title': 'Error loading data...'}
    # print cur.fetchone()
    for core_id, book_title, isbn, page_count, publisher_name, book_description, publication_date, publication_date_fmt, cover_name, avg_rating in cur:
        book_info = {'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'), 'isbn': isbn,
                     'num_pages': page_count, 'publisher_name': publisher_name.decode('utf8', 'xmlcharrefreplace'), 'cover_name': cover_name, 'authors': [],
                     'subjects': [], 'avg_rating': avg_rating, 'book_description': book_description,
                     'publication_date': publication_date, 'publication_date_fmt': publication_date_fmt, 'containing_lists': [], 'reading_logs': [], 'reviews': []}
        # print book_info

    cur.execute('''
    SELECT author_name
    FROM author JOIN authorship USING (author_id)
    WHERE core_id = %s
    ''', (book_info['core_id'],))
    author_info = []
    for author_name in cur:
        # print author_name
        author_info.append(author_name[0].decode('utf8', 'xmlcharrefreplace'))
    book_info['authors'] = author_info
    print book_info['authors']
    book_info['author_count'] = cur.rowcount
    # print book_info['author']

    # Get subjects
    cur.execute('''
    SELECT subject_name
    FROM subject_genre JOIN book_categorization USING (subject_id)
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
            try:
                book_info['containing_lists'].append({'id': list_id, 'list_name': list_name, 'user_id': user_id,
                                                  'login_name': login_name, 'date_created': date_created, 'num_books': num_books})
            except KeyError:
                print "Missing book_info for book_id %s?" % book_id

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
    if (user_id):
        cur.execute('''
        SELECT rating
        FROM ratings
        WHERE book_id = %s AND rater = %s
        ''', (book_info['core_id'], user_id))
        if cur.rowcount > 0:
            book_info['user_rating'] = cur.fetchone()[0]
    return book_info


def add_rating(cur, book_id, rating, user_id):
    print "Book id for adding rating: %s" % book_id
    book_info = get_book(cur, book_id)
    # try:
    cur.execute('''
        SELECT ratings
        FROM ratings
        WHERE book_id = %s AND rater = %s
    ''', (book_id, user_id))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        cur.execute('''
          UPDATE ratings SET rating = %s
          WHERE book_id = %s AND rater = %s
          RETURNING ratings
        ''', (rating, book_info['core_id'], user_id))
        if cur.rowcount == 1:
            message = "Rating of %s updated for %s!" % (rating, book_info['title'])
        else:
            message = "Unknown error!"
    # except Exception, e:
    #     message = errorcodes.lookup(e.pgcode[:2])
    else:
        cur.execute('''
          INSERT INTO ratings (book_id, rater, rating, date_rated)
          VALUES(%s, %s, %s, current_timestamp)
          RETURNING ratings
        ''', (book_info['core_id'], user_id, rating))
        if cur.rowcount == 1:
            message = "Rating of %s saved for %s!" % (rating, book_info['title'])
        else:
            message = "Unknown error!"

    # else:
    #     message = "User not currently authenticated!"

    return message

def remove_rating(cur, book_id, user_id):
    print "Book id for removing rating: %s" % book_id
    book_info = get_book(cur, book_id)
    # try:
    cur.execute('''
        DELETE FROM ratings
        WHERE book_id = %s AND rater = %s
    ''', (book_id, user_id))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "Rating removed for %s!" % (book_info['title'])
    else:
        message = "Unknown error!"
    # except Exception, e:
    #     message = errorcodes.lookup(e.pgcode[:2])


    # else:
    #     message = "User not currently authenticated!"

    return message


def edit_book(cur, book_id, form):
    print form

    update_status = True

    author_names = {}
    subjects = []
    for key, value in form.iteritems():
        if 'inputBookAuthor' in key:
            author_names[key[15:]] = value #try to keep position
        if 'inputBookSubject' in key:
            subject.append(value)
            
    publication_date = form['inputBookPubDate']
    isbn = form['inputBookISBN']
    page_count = form['inputBookPageCount']
    book_title = form['inputBookTitle']
    book_description = form['inputBookDescription']
    
    cur.execute('''
    UPDATE books SET 
    publication_date = %s
    ISBN = %s
    book_type = %s
    page_count = %s
    book_title = %s
    book_description = %s
    WHERE book_id = %s
    RETURNING book_id
    ''', (publication_date, isbn, page_count, book_title, book_description, book_id))
    if cur.rowcount == 1:
        message = "Book %s updated!" % book_info['title']

    else:
        message = "Unknown error!"    

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
    return True, message



def get_books_in_list(cur,lid,user_id=None):
    cur.execute('''
        SELECT core_id, book_title, book_description, isbn, page_count, COALESCE(cover_name,'_placeholder') as cover_name, AVG(rating) as avg_rating, COUNT(DISTINCT log_id) as num_readers
        FROM book_core
        JOIN books USING (core_id)
        LEFT JOIN ratings ON core_id = ratings.book_id
        JOIN user_log ON core_id = user_log.book_id
        JOIN book_list ON core_id = book_list.book_id
        WHERE list_id = %s
        GROUP BY core_id, book_title, book_description, cover_name, isbn, page_count, publication_date
    ''', ( lid,))
    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for core_id, book_title, description, isbn, page_count, cover_name, avg_rating, num_readers in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'),
                          'cover_name': cover_name, 'authors': [], 'subjects': [], 'isbn': isbn, 'num_pages': page_count,
                          'num_readers': num_readers, 'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            author_info.append(str(author_name[0]).decode('utf8', 'xmlcharrefreplace'))

        book['authors'] = author_info
        # print book['authors']
        cur.execute('''
        SELECT subject_name
        FROM subject_genre JOIN book_categorization USING (subject_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        # subject_info = []
        # print cur.fetchone()
        for subject_name in cur:
            book['subjects'].append(subject_name[0].decode('utf8', 'xmlcharrefreplace'))
        # book['subjects'] = subject_info
        if (user_id):
            cur.execute('''
            SELECT rating
            FROM ratings
            WHERE book_id = %s AND rater = %s
            ''', (book['core_id'], user_id))
            if cur.rowcount > 0:
                book['user_rating'] = cur.fetchone()[0]
        # print book['subjects']
    return book_info