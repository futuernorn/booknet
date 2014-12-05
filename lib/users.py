import bcrypt
from psycopg2 import errorcodes
import books
USERS_PER_PAGE = 15;


QUERIES = {
    'reviews_count': '''
        SELECT COUNT(*) FROM review;
    ''',
    'reviews_by_book_count': '''
        SELECT COUNT(*) FROM review WHERE book_id = %s;
    ''',
    'select_user_where': '''
        SELECT user_id, login_name, level_name, COALESCE(is_followed, FALSE) as is_followed, COUNT(DISTINCT book_list.book_id) as num_unique_list_books,
        COUNT(DISTINCT user_log.book_id) as num_total_books_read, COUNT(DISTINCT log_id) as num_unique_books_read, COUNT(DISTINCT review_id) as num_reviews
        FROM booknet_user
        LEFT JOIN review ON user_id = reviewer
        LEFT JOIN list USING (user_id)
        LEFT JOIN book_list USING (list_id)
        LEFT JOIN user_level USING (level_id)
        LEFT JOIN user_log ON user_id = reader
        LEFT JOIN  ( SELECT user_followed, is_followed FROM follow WHERE follower = %s ) is_followed_table ON user_id = user_followed
        WHERE user_id = %s
        GROUP BY user_id, login_name, level_name, is_followed
    ''',
    'select_user_lists': '''
      SELECT list_id, list_name, COUNT(DISTINCT book_id) as num_books
      FROM list JOIN book_list USING (list_id)
      WHERE user_id = %s
      GROUP BY list_id, list_name;
    ''',
    'select_user_logs': '''
      SELECT log_id, log_text, to_char(date_started,'Mon. DD, YYYY') as date_started,
      to_char(date_completed,'Mon. DD, YYYY') as date_completed
      FROM user_log
      WHERE reader = %s AND book_id = %s;
    ''',
    'select_request_on_book_info': '''
        SELECT request_id, request_on_book_id, request_type, book_id, request_text, book_title, login_name, user_id, to_char(date_requested,'Mon. DD, YYYY') as date_requested
        FROM request
        JOIN request_on_book USING (request_id)
        JOIN books USING (book_id)
        JOIN book_core USING (core_id)
        JOIN booknet_user USING (user_id)
        WHERE status = 'Awaiting Review'
    ''',
    'select_one_request_on_book_info': '''
        SELECT request_id, request_on_book_id, request_type, book_id, request_text, book_title, login_name, user_id, to_char(date_requested,'Mon. DD, YYYY') as date_requested
        FROM request
        JOIN request_on_book USING (request_id)
        JOIN books USING (book_id)
        JOIN book_core USING (core_id)
        JOIN booknet_user USING (user_id)
        WHERE request_id = %s
    '''
}


def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM booknet_user ;
    ''')
    total_users = cur.fetchone()[0];
    total_pages = ((total_users-1) / USERS_PER_PAGE) + 1;
    return total_pages

def logout_user():
    raise NotImplementedError

#Users need to be able to follow other users, and see a news feed containing the new reviews, reads, etc. by the users they follow.
def get_user_feed(cur,user_id):
    cur.execute('''
        SELECT user_id, login_name, level_name, COALESCE(is_followed, FALSE), COUNT(DISTINCT review_id) as num_reviews, COUNT(DISTINCT list_id) as num_lists
        FROM booknet_user
        JOIN review ON user_id = reviewer
        JOIN list USING (user_id)
        JOIN user_level USING (level_id)
        LEFT JOIN  follow ON user_id = user_followed
        WHERE follower = %s
        GROUP BY user_id, login_name, level_name, is_followed
    ''', (user_id,))
    user_info = {'following': []}

    for user_id, login_name, level_name, is_followed, num_reviews, num_lists in cur:
        user_info['following'].append({'user_id':user_id, 'name': login_name, 'access_level': level_name, 'num_reviews': num_reviews,
                          'num_lists': num_lists, 'num_books_read': None, 'is_followed': is_followed, 'reviews':[]})




    # for user_followed, login_name, is_followed in cur:
    #     user_info['following'].append({'user_id': user_followed, 'name': login_name, 'is_followed': is_followed, 'reviews':[]})

    for user in user_info['following']:
        cur.execute('''
            SELECT review_id, book_id, to_char(date_reviewed,'Mon. DD, YYYY') as date_reviewed, book_title, review_text
            FROM review
            JOIN book_core ON book_id = core_id
            WHERE reviewer = %s AND date_reviewed > NOW() - INTERVAL '60 days'
        ''', (user['user_id'],))
        for review_id, book_id, date_reviewed, book_title, review_text in cur:
            user['reviews'].append({'review_id': review_id, 'book_id': book_id, 'date_reviewed': date_reviewed,
                                    'review_text': review_text, 'book_title': book_title.decode('utf8', 'xmlcharrefreplace')})

    return user_info
def get_user(cur,user_id,current_user_id=None):
    query = QUERIES['select_user_where'] % ('%s', '%s')
    cur.execute(query, (current_user_id, user_id))
    user_info = {}
    for user_id, login_name, level_name, is_followed, num_unique_list_books, num_total_books_read, num_unique_books_read, num_reviews in cur:
    # is_followed = False
        user_info = ({'id':user_id, 'name': login_name, 'access_level': level_name, 'num_reviews': num_reviews,
                      'num_unique_list_books': num_unique_list_books, 'num_total_books_read': num_total_books_read,
                      'num_unique_books_read': num_unique_books_read, 'is_followed': is_followed})


    # get lists
    cur.execute('''
        SELECT list_id, list_name, to_char(date_created,'Mon. DD, YYYY') as date_created, COUNT(book_id) as num_books
        FROM list
        JOIN book_list USING (list_id)
        WHERE user_id = %s
        GROUP BY list_id, list_name, date_created
    ''', (user_id,))
    user_info['lists'] = []
    for list_id, list_name, date_created, num_books in cur:
        user_info['lists'].append({'list_id': list_id, 'list_name': list_name, 'date_created': date_created, 'num_books': num_books})

    # get reviews
    cur.execute('''
        SELECT review_id, book_core.core_id, book_id, book_title, reviewer, login_name, to_char(date_reviewed,'Mon. DD, YYYY'), review_text
        FROM review
        JOIN book_core ON review.book_id = book_core.core_id
        JOIN books USING (book_id)
        JOIN booknet_user ON reviewer = user_id
        WHERE reviewer = %s
    ''', (user_id,))
    user_info['reviews'] = []
    for  review_id, core_id, book_id, book_title, reviewer, login_name, date_reviewed, review_text in cur:
        user_info['reviews'].append({'core_id':core_id, 'id':review_id, 'book_id': book_id, 'date_reviewed': date_reviewed,
                                     'review_text':review_text, 'book_title':book_title.decode('utf8', 'xmlcharrefreplace')})

    # get logs
    cur.execute('''
        SELECT log_id, core_id, book_title, to_char(date_started,'Mon. DD, YYYY') as date_started, to_char(date_completed,'Mon. DD, YYYY') as date_completed
        FROM user_log
        JOIN book_core ON book_id = core_id
        WHERE reader = %s
        GROUP BY log_id, core_id, book_title, date_started, date_completed
    ''', (user_id,))
    user_info['reading_logs'] = []
    for log_id, core_id, book_title, date_started, date_completed in cur:
        user_info['reading_logs'].append({'log_id': log_id, 'core_id': core_id, 'book_title': book_title.decode('utf8', 'xmlcharrefreplace'), 'date_started': date_started,
                                         'date_completed': date_completed})

    # get logs by year
    cur.execute('''
        SELECT DISTINCT EXTRACT(YEAR FROM date_completed) as year
        FROM user_log
        WHERE reader = %s
    ''', (user_id,))

    log_years = []
    for year in cur:
        year = int(year[0])
        log_years.append(year)

    user_info['reading_logs_by_year'] = []
    for year in log_years:
        cur.execute('''
            SELECT COUNT(DISTINCT log_id) as num_logs, COUNT(DISTINCT book_id) as num_books, SUM(pages_read) as num_pages_read
            FROM user_log
            WHERE reader = %s AND EXTRACT(YEAR FROM date_completed) = %s
        ''', (user_id,year))
        # user_info['reading_log'] = []
        for num_logs, num_books, num_pages_read in cur:
            user_info['reading_logs_by_year'].append({'year': year, 'num_logs': num_logs, 'num_books': num_books, 'num_pages_read': num_pages_read})
    return user_info

def validate_login(cur, form):
    username = form['username']
    posted_password = form['password']
    cur.execute('''
      SELECT user_id, login_name, password
      FROM booknet_user
      WHERE login_name = %s
    ''', (username,))
    if cur.rowcount != 1:
      return False
    else:
      for id, login_name, password in cur:
        print username
      
      print bcrypt
      if bcrypt.checkpw(posted_password, password):
          return id
      else:
          return False

def register_user(cur, form):
    username = form['username']
    email = form['email']
    posted_password = form['password']
    password = bcrypt.hashpw(posted_password, bcrypt.gensalt())
    try:
        cur.execute('''
          INSERT INTO booknet_user (login_name, email, password, level_id, date_created, is_active)
          VALUES(%s, %s, %s, 1, current_timestamp, true)
          RETURNING user_id
        ''', (username,email,password))
        if cur.rowcount == 1:
            user_id = cur.fetchone()[0]
            return True, user_id, None
    except Exception, e:
        return False, None, errorcodes.lookup(e.pgcode[:2])

def get_all_users(cur,page,user_id=None):
    return get_user_range(cur,((page - 1) * USERS_PER_PAGE), USERS_PER_PAGE, user_id)

def get_user_range(cur,start,amount, user_id=None):
    cur.execute('''
        SELECT user_id, login_name, level_name, COALESCE(is_followed, FALSE), COUNT(DISTINCT review_id) as num_reviews, COUNT(DISTINCT list_id) as num_lists
        FROM booknet_user
        JOIN review ON user_id = reviewer
        JOIN list USING (user_id)
        JOIN user_level USING (level_id)
        LEFT JOIN  ( SELECT user_followed, is_followed FROM follow WHERE follower = %s ) is_followed_table ON user_id = user_followed
        GROUP BY user_id, login_name, level_name, is_followed
        LIMIT %s OFFSET %s
    ''', (user_id, amount, start))
    user_info = []
# LEFT JOIN  ( SELECT user_followed, is_followed FROM follow WHERE follower = %s ) is_followed_table ON user_id = user_followed
    # print "Retrieved %s book rows..." % cur.rowcount
    for user_id, login_name, level_name, is_followed, num_reviews, num_lists in cur:
        # is_followed = False
        user_info.append({'id':user_id, 'name': login_name, 'access_level': level_name, 'num_reviews': num_reviews,
                          'num_lists': num_lists, 'num_books_read': None, 'is_followed': is_followed})
    for user in user_info:
        # print user
        cur.execute('''
            SELECT COUNT(log_id) as num_books_read
            FROM user_log
            WHERE reader = %s
        ''', (user['id'],))
        for num_books_read in cur:
            user['num_books_read'] = num_books_read[0]
    return user_info

def get_user_lists(cur,user_id):
    lists = {}
    query = QUERIES['select_user_lists'] % '%s'
    cur.execute(query, (user_id,))

    for list_id, list_name, num_books in cur:
        lists[cur.rownumber] = {'list_id': list_id, 'list_name': list_name, 'num_books': num_books};

    return lists

def get_user_logs(cur, user_id, book_id):
    logs = {}
    query = QUERIES['select_user_logs'] % ('%s', '%s')
    cur.execute(query, (user_id, book_id))

    for log_id, log_text, date_completed, date_started in cur:
        logs[cur.rownumber] = {'log_id': log_id, 'log_text': log_text, 'date_completed': date_completed, 'date_started': date_started};

    return logs

def approve_request(cur, request_id, user_id):
    print "approve_request started..."
    update_status = True
    book_id = 0
    message = []
    query = QUERIES['select_one_request_on_book_info'] % '%s'
    cur.execute(query, (request_id,))

    for request_id, request_on_book_id, request_type, book_id, request_text, book_title, login_name, user_id, date_requested in cur:
        update_status, set_book_active_message = books.set_book_active(cur,book_id)
        message.append(set_book_active_message)
        cur.execute('''
            UPDATE request SET
            status = '0'
            WHERE request_id = %s
            RETURNING status
        ''', (request_id,))
        return update_status, message, book_id
    return update_status, message, book_id


def get_moderation_info(cur):
    # mod_info.total_requests }}</h4> </li>
    #             <li class="list-group-item"><h4># Incomplete Requests: {{ mod_info.incomplete_requests }}</h4></li>
    #             <li class="list-group-item"><h4># Completed Requests: {{ mod_info.completed_requests



    mod_info = {'requests': []}
    query = QUERIES['select_request_on_book_info']
    cur.execute(query)

    for request_id, request_on_book_id, request_type, book_id, request_text, book_title, login_name, user_id, date_requested in cur:

        mod_info['requests'].append({'request_id': request_id, 'request_on_book_id': request_on_book_id, 'request_type': request_type,
                               'book_id': book_id, 'request_text': request_text, 'book_title': book_title, 'requester': login_name,
                               'user_id': user_id, 'date_requested': date_requested})
    print mod_info
    return mod_info
#################### Following #########################################################################################
def add_follower(cur, followee, follower):

    # user_info = get_user(cur,  followee.get_id())
    # try:
    cur.execute('''
        SELECT follow_id
        FROM follow
        WHERE user_followed = %s AND follower = %s
    ''', (followee.get_id(),follower))
    if cur.rowcount == 1:
        message = "%s already being followed!" % followee.name

    else:
        cur.execute('''
          INSERT INTO follow (follower, user_followed, date_followed, is_followed)
          VALUES(%s, %s, current_timestamp, True)
          RETURNING follow_id
        ''', (follower, followee.get_id()))
        if cur.rowcount == 1:
            message = "Now following %s!" % followee.name
        else:
            message = "Unknown error!"

    # else:
    #     message = "User not currently authenticated!"

    return message

def remove_follower(cur, followee, follower):

    # user_info = get_user(cur, followee.get_id())
    # try:
    cur.execute('''
        DELETE FROM follow
        WHERE user_followed = %s AND follower = %s
    ''', (followee.get_id(),follower))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "No longer following %s!" % followee.name
    else:
        message = "Unknown error!"
    # except Exception, e:
    #     message = errorcodes.lookup(e.pgcode[:2])


    # else:
    #     message = "User not currently authenticated!"

    return message



