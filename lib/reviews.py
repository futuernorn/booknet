"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

import books

REVIEWS_PER_PAGE = 15;

QUERIES = {
    'reviews_count': '''
        SELECT COUNT(*) FROM review;
    ''',
    'reviews_by_book_count': '''
        SELECT COUNT(*) FROM review WHERE book_id = %s;
    ''',
    'select_reviews_where': '''
        SELECT review_id, book_core.core_id, book_id, book_title, reviewer, login_name, to_char(date_reviewed,'Mon. DD, YYYY'), review_text
        FROM review
        JOIN book_core ON review.book_id = book_core.core_id
        JOIN books USING (book_id)
        JOIN booknet_user ON reviewer = user_id
        %s
        LIMIT %s OFFSET %s
    '''
}

def get_total_pages(cur,query):
    cur.execute(query)
    total_books = cur.fetchone()[0];
    total_pages = (total_books / REVIEWS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_reviews(cur, amount):
    return get_review_range(cur,0,amount)

def get_review_range(cur,start,amount):

    total_pages = get_total_pages(cur, QUERIES['reviews_count'])
    query = QUERIES['select_reviews_where'] % ('', '%s', '%s')
    cur.execute(query, (amount, start))
    review_info = []
    for  review_id, core_id, book_id, book_title, reviewer, login_name, date_reviewed, review_text in cur:
        review_info.append({'core_id':core_id, 'id':review_id, 'book_id': book_id, 'book_title':book_title.decode('utf8', 'xmlcharrefreplace'), 'reviewer':reviewer, 'reviewer_name': login_name, 'date_reviewed': date_reviewed, 'review_text':review_text})

    return total_pages, review_info

def get_reviews_by_book(cur, start, amount, bid, current_user_id):

    total_pages = get_total_pages(cur, QUERIES['reviews_by_book_count'] % bid)
    query = QUERIES['select_reviews_where'] % ('WHERE review.book_id = %s', '%s', '%s')
    book_info = books.get_book(cur,bid,current_user_id)

    cur.execute(query, (bid, amount, start))

    review_info = {'book_info': book_info, 'reviews': []}
    for  review_id, core_id, book_id, book_title, reviewer, login_name, date_reviewed, review_text in cur:
        review_info['reviews'].append({'core_id':core_id, 'id':review_id, 'book_id': book_id, 'book_title':book_title.decode('utf8', 'xmlcharrefreplace'), 'reviewer':reviewer, 'reviewer_name': login_name, 'date_reviewed': date_reviewed, 'review_text':review_text})

    return total_pages, review_info

def get_review(cur,review_id):
    cur.execute('''
        SELECT review_id, core_id, book_id, book_title, reviewer, login_name, to_char(date_reviewed,'Mon. DD, YYYY'), review_text
        FROM review
        JOIN books USING (book_id)
        JOIN book_core USING (core_id)
        JOIN booknet_user ON reviewer = user_id
        WHERE review_id = %s
    ''', (review_id,))
    review_info = {}
    for  review_id, core_id, book_id, book_title, reviewer, login_name, date_reviewed, review_text in cur:
        review_info = {'core_id':core_id, 'id':review_id, 'book_id': book_id, 'book_title':book_title.decode('utf8', 'xmlcharrefreplace'),
                       'user_id':reviewer, 'reviewer': login_name, 'date_reviewed': date_reviewed, 'review_text':review_text}

    review_info['book'] = books.get_book(cur, review_info['book_id'])
    return review_info


###################### Modifications ##################################################################################
def add_review(cur, book_id, user_id, form):
    message = []
    entry_status = True
    review_id = 0
    try:
        message.append(books.add_rating(cur, book_id, form['rating'], user_id))
    except KeyError:
        # no rating entered
        pass

    try:
        cur.execute('''
          INSERT INTO review (book_id, reviewer, review_text, date_reviewed)
          VALUES(%s, %s, %s, current_timestamp)
          RETURNING review_id
        ''', (book_id, user_id, form['review_input']))
        if cur.rowcount == 1:
            message.append("Review of saved!")
            review_id = cur.fetchone()[0]
        else:
            message.append("Unknown error!")
            entry_status = False
    except KeyError:
        message.append("No review text provided!")
        entry_status = False
    # except:
    #     message = "Unknown error!"
    #     entry_status = False

    return entry_status, message, review_id
