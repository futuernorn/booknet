"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

BOOKS_PER_PAGE = 50;

def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM books;
    ''')
    total_books = cur.fetchone()[0];
    total_pages = (total_books / BOOKS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_books(cur, amount):
    return get_book_range(cur,0,amount)

def get_all_books(cur, page, sorting, sort_direction):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_book_range(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, sorting, sort_direction)

def get_book_range(cur,start,amount,sorting=None, sort_direction=None):
    if sorting and sort_direction:
        order_by = "ORDER BY %s %s " % (sorting,sort_direction) # this is stupid
    else:
        order_by = ""

    cur.execute(
        "SELECT core_id, book_id, picture, book_title, book_description, isbn, EXTRACT(YEAR from publication_date) as pub_year, ROUND(AVG(rating)) as avg_rating "+
        "FROM books "+
        "JOIN book_core USING (core_id) "+
        "LEFT JOIN ratings USING (book_id) "+
        "GROUP BY core_id, book_id, picture, book_title, book_description, isbn, publication_date "+
        order_by+
        "LIMIT %s OFFSET %s"
    , ( amount, start))
    book_info = []
    for core_id, id, picture, book_title, description, isbn, pub_year, rating in cur:
        book_info.append({'core_id':core_id, 'id': id, 'picture':'', 'title': str(book_title), 'isbn':isbn, 'pub_year': pub_year,
                          'authors':[], 'rating':rating})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            book['authors'].append(author_name)
        print book['authors']

    # print book_info['author']

    return book_info


def get_book(cur,book_id):
    cur.execute('''
        SELECT core_id, book_id, picture, book_title, book_description, isbn, EXTRACT(YEAR from publication_date) as pub_year, ROUND(AVG(rating)) as avg_rating
        FROM books
        JOIN book_core USING (core_id)
        LEFT JOIN ratings USING (book_id)
        WHERE book_id = %s
        GROUP BY core_id, book_id, picture, book_title, book_description, isbn, publication_date
    ''', (book_id,))
    book_info = []
    for core_id, id, picture, book_title, description, isbn, pub_year, rating in cur:
        book_info.append({'core_id':core_id, 'id': id, 'picture':'', 'title': str(book_title), 'isbn':isbn, 'pub_year': pub_year,
                          'authors':[], 'rating':rating})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE core_id = %s
        ''', (book['core_id'],))
        author_info = []
        for author_name in cur:
            book['authors'].append(author_name)
        print book['authors']

    # print book_info['author']

    return book_info
