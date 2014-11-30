"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'



REVIEWS_PER_PAGE = 15;

def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM review;
    ''')
    total_reviews = cur.fetchone()[0];
    total_pages = (total_reviews / REVIEWS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_reviews(cur, amount):
    return get_review_range(cur,0,amount)

def get_all_reviews(cur, page):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_review_range(cur,((page - 1) * REVIEWS_PER_PAGE), REVIEWS_PER_PAGE)

def get_review_range(cur,start,amount):
    cur.execute('''
        SELECT review_id, core_id, book_id, book_title, reviewer, login_name, to_char(date_reviewed,'Mon. DD, YYYY'), review_text
        FROM review
        JOIN books USING (book_id)
        JOIN book_core USING (core_id)
        JOIN booknet_user ON reviewer = user_id
        LIMIT %s OFFSET %s
    ''', (amount, start))
    review_info = []
    for  review_id, core_id, book_id, book_title, reviewer, login_name, date_reviewed, review_text in cur:
        review_info.append({'core_id':core_id, 'review_id':review_id, 'book_id': book_id, 'book_title':book_title.decode('utf8', 'xmlcharrefreplace'), 'reviewer':reviewer, 'reviewer_name': login_name, 'date_reviewed': date_reviewed, 'review_text':review_text})

    return review_info
