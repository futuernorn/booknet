"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

from psycopg2 import errorcodes

BOOKS_PER_PAGE = 15;

def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM book_core JOIN books USING (core_id);
    ''')
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
    if sorting and sort_direction:
        order_by = "ORDER BY %s %s " % (sorting,sort_direction) # this is stupid
    else:
        order_by = ""
    # cur.execute(
    #     "SELECT core_id, book_title, book_description "+
    #     "FROM book_core "+
    #     "JOIN books USING (core_id) "
    # )
    # print "Total rows retrieved: %s..." % cur.rowcount
    cur.execute(
        "SELECT core_id, book_title, book_description, COALESCE(cover_name,'placeholder-S.jpg') as cover_name, AVG(rating) as avg_rating "+
        "FROM book_core "+
        "JOIN books USING (core_id) "+
        # "JOIN book_categorization USING (core_id) "+
        # "JOIN subject_genre USING (subject_id) "+
        "LEFT JOIN ratings ON core_id = ratings.book_id "+
        # "GROUP BY core_id, book_id, picture, book_title, book_description, isbn, publication_date "+
        # order_by+
        # "SELECT DISTINCT core_id, book_title, book_description,  ROUND(AVG(rating)) as avg_rating "+
        # "FROM books "+
        # "JOIN book_core USING (core_id) "+
        # "JOIN book_categorization USING (core_id) "+
        # "JOIN subject_genre USING (subject_id) "+
        # "LEFT JOIN ratings USING (book_id) "+
        "GROUP BY core_id, book_title, book_description, cover_name " +
        # order_by+
        "LIMIT %s OFFSET %s"
    , ( amount, start))
    book_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for core_id, book_title, description, cover_name, avg_rating in cur:
        if avg_rating:
            discrete_rating = round(avg_rating*2) / 2
        else:
            discrete_rating = 0
        book_info.append({'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'), 'cover_name': cover_name, 'authors': [], 'subjects': [],
                          'avg_rating': avg_rating, 'discrete_rating': discrete_rating, 'user_rating': None})
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


def get_book(cur,book_id):
    cur.execute('''
        SELECT DISTINCT core_id,book_title
        FROM books
        JOIN book_core USING (core_id)
        WHERE core_id = %s
    ''', (book_id,))
    book_info = {'core_id': book_id, 'title': 'Error loading data...'}
    # print cur.fetchone()
    for core_id, book_title in cur:
        book_info = {'core_id':core_id, 'title': str(book_title).decode('utf8', 'xmlcharrefreplace'), 'authors': [], 'subjects': [], 'avg_rating': 0}
        print book_info

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

    print book_info['subjects']

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
