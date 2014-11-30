import bcrypt
from psycopg2 import errorcodes

USERS_PER_PAGE = 15;

def get_total_pages(cur):
    cur.execute('''
        SELECT COUNT(*)
        FROM "user" ;
    ''')
    total_users = cur.fetchone()[0];
    total_pages = ((total_users-1) / USERS_PER_PAGE) + 1;
    return total_pages

def logout_user():
    raise NotImplementedError


def get_user(cur,id):
    cur.execute('''
        SELECT *
        FROM user
        WHERE user_id = %s
    ''', (id,))
    user_row = cur.fetchone()[0]
    print user_row
    return user_row



def validate_login(cur, form):
    username = form['username']
    posted_password = form['password']
    cur.execute('''
      SELECT user_id, login_name, password
      FROM "user"
      WHERE login_name = %s
    ''', (username,))
    if cur.rowcount != 1:
      return False
    else:
      for id, login_name, password in cur:
        print username
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
          INSERT INTO "user" (login_name, email, password, level_id, date_created, is_active)
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
        SELECT user_id, login_name, level_name, COUNT(DISTINCT review_id) as num_reviews, COUNT(DISTINCT list_id) as num_lists
        FROM "user"
        JOIN review ON user_id = reviewer
        JOIN list USING (user_id)
        JOIN user_level USING (level_id)
        GROUP BY user_id, login_name, level_name
        LIMIT %s OFFSET %s
    ''', (amount, start))
    user_info = []
# LEFT JOIN  ( SELECT user_followed, is_followed FROM follow WHERE follower = %s ) is_followed_table ON user_id = user_followed
    # print "Retrieved %s book rows..." % cur.rowcount
    for user_id, login_name, level_name, num_reviews, num_lists in cur:
        is_followed = False
        user_info.append({'id':user_id, 'name': login_name, 'access_level': level_name, 'num_reviews': num_reviews, 'num_lists': num_lists, 'is_followed': is_followed})

    return user_info

def add_follower(cur, followee, follower):

    user_info = get_user(cur, followee)
    # try:
    cur.execute('''
        SELECT follow_id
        FROM follow
        WHERE user_followed = %s AND follower = %s
    ''', (followee,follower))
    if cur.rowcount == 1:
        message = "%s already being followed!" % user_info['login_name']

    else:
        cur.execute('''
          INSERT INTO follow (follower, user_followed, date_followed, is_followed)
          VALUES(%s, %s, current_timestamp, True)
          RETURNING follow_id
        ''', (follower, followee))
        if cur.rowcount == 1:
            message = "Now following %s!" % user_info['login_name']
        else:
            message = "Unknown error!"

    # else:
    #     message = "User not currently authenticated!"

    return message

def remove_follower(cur, followee, follower):

    user_info = get_user(cur, followee)
    # try:
    cur.execute('''
        DELETE FROM follow
        WHERE user_followed = %s AND follower = %s
    ''', (followee,follower))
    # first two queries should be able to be combined
    if cur.rowcount == 1:
        message = "No longer following %s!" % user_info['login_name']
    else:
        message = "Unknown error!"
    # except Exception, e:
    #     message = errorcodes.lookup(e.pgcode[:2])


    # else:
    #     message = "User not currently authenticated!"

    return message