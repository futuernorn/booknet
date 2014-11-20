import bcrypt


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



def validate_login(cur, username, posted_password):
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



