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

def get_all_users(cur,page,user_id):
    return get_user_range(cur,((page - 1) * USERS_PER_PAGE), USERS_PER_PAGE, user_id)

def get_user_range(cur,start,amount, user_id=None):
    cur.execute('''
        SELECT user_id, login_name, level_name
        FROM "user"
        JOIN user_level USING (level_id)
        LIMIT %s OFFSET %s
    ''', ( amount, start))
    user_info = []
    # print "Retrieved %s book rows..." % cur.rowcount
    for user_id, login_name, level_name in cur:
        user_info.append({'id':user_id, 'name': login_name, 'access_level': level_name})

    return user_info