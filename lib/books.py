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

def get_all_books(cur, page):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_book_range(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE)

def get_book_range(cur,start,amount):
    cur.execute('''
        SELECT core_id, book_id, picture, book_title, book_description, isbn, EXTRACT(YEAR from publication_date) as pub_year, ROUND(AVG(rating)) as avg_rating
        FROM books JOIN book_core USING (core_id) JOIN ratings USING (book_id)
        GROUP BY core_id, book_id, picture, book_title, book_description, isbn, pub_year
        LIMIT %s OFFSET %s
    ''', (amount, start))
    book_info = []
    for core_id, id, picture, book_title, description, isbn, pub_year, rating in cur:
        book_info.append({'core_id':core_id, 'id': id, 'picture':'', 'title': str(book_title), 'isbn':isbn, 'pub_year': pub_year,
                          'authors':[], 'rating':rating})
    for book in book_info:
        cur.execute('''
        SELECT author_name
        FROM author JOIN authorship USING (author_id)
        WHERE book_core = %s
        ''', (book['core_id']))
        author_info = []
        for author_name in cur:
            author_info.append(author_name)
        book_info['authors'] = author_info


    return book_info
