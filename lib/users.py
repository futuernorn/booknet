import bcrypt
from psycopg2 import errorcodes
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


