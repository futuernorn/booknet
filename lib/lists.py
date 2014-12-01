"""
Functions for working with the books database.
"""
__author__ = 'Jeffrey Hogan'

from psycopg2 import errorcodes

LISTS_PER_PAGE = 15;

def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM list;
    ''')
    total_lists = cur.fetchone()[0];
    total_pages = (total_lists / LISTS_PER_PAGE) + 1;
    return total_pages

def get_spotlight_lists(cur, amount):
    return get_list_range(cur,0,amount)

def get_all_lists(cur, page, user_id=None):
    """
    Get a list of all article IDs, titles, proceeding titles, authors, and year of publication.
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """
    return get_list_range(cur,((page - 1) * BOOKS_PER_PAGE), BOOKS_PER_PAGE, user_id= None)

def get_list_range(cur,start,amount, user_id=None):
    cur.execute('''
        SELECT list_id, list_name, user_id, date_created, list_description
        FROM list
        JOIN booknet_user USING (user_id)
        LIMIT %s OFFSET %s
    ''', ( amount, start))
    list_info = []

    for list_id, list_name, user_id, date_created, list_description in cur:
        list_info.append({'id':list_id, 'list_name': list_name, 'user_id': user_id, 'date_created': date_created, 'description': list_description})

    return list_info


def get_list(cur,list_id):
    cur.execute('''
        SELECT list_id, list_name, user_id, date_created, list_description
        FROM list
        JOIN booknet_user USING (user_id)
        WHERE list_id = %s
    ''', (list_id,))
    list_info = []

    for list_id, list_name, user_id, date_created, list_description in cur:
        list_info.append({'id':list_id, 'list_name': list_name, 'user_id': user_id, 'date_created': date_created, 'description': list_description})

    return list_info

def create_list(cur, list_name, description, user_id):
    
    cur.execute('''
        SELECT list_id
        FROM list
        WHERE list_name = %s AND user_id = %s
    ''', (list_name, user_id))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "%s has already created a list with this name (%s)!" % (user_id, list_name)
    else:
        cur.execute('''
          INSERT INTO list (list_name, user_id, date_created, list_description)
          VALUES(%s, %s, current_timestamp, %s)
          RETURNING booklist_id
        ''', (list_name, user_id, description))
        if cur.rowcount == 1:
            message = "Created new list: %s!" % list_name
        else:
            message = "Unknown error!"

    # else:
    #     message = "User not currently authenticated!"

    return message

def delete_list(cur,list_id,user_id):


def add_book_to_list(cur, book_id, list_id, user_id):
    print "Book id for adding list: %s" % book_id
    book_info = books.get_book(cur, book_id)
    # try:
    cur.execute('''
        SELECT booklist_id
        FROM book_list
        WHERE book_id = %s AND list_id = %s
    ''', (book_id, list_id))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "%s already in list %s!" % (book_info['title'], list_id)
    else:
        cur.execute('''
          INSERT INTO book_list (book_id, list_id, date_added)
          VALUES(%s, %s, current_timestamp)
          RETURNING booklist_id
        ''', (book_info['core_id'], list_id))
        if cur.rowcount == 1:
            message = "%s added to list %s!" % (book_info['title'], list_id)
        else:
            message = "Unknown error!"

    # else:
    #     message = "User not currently authenticated!"

    return message

def remove_book_from_list(cur, book_id, list_id):
    print "Book id for removing rating: %s" % book_id
    book_info = get_book(cur, book_id)
    # try:
    cur.execute('''
        DELETE FROM book_list
        WHERE book_id = %s AND list_id = %s
    ''', (book_id, list_id))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "Book removed from list %s!" % (book_info['title'], list_id)
    else:
        message = "Unknown error!"
    # except Exception, e:
    #     message = errorcodes.lookup(e.pgcode[:2])


    # else:
    #     message = "User not currently authenticated!"

    return message
