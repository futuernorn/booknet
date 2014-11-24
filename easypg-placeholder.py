"""
EasyPG Dummy - for testing in envrionments without the ability to install psycopg

"""

import os.path
from contextlib import closing, contextmanager



@contextmanager
def cursor(**kwargs):
    cur = Cursor()
    yield cur


class Cursor:
    rowcount = 1
    def fetchone(self):
        return [1]

    def execute(self, sql_query, *variables):
        log_file = open('easypg-placeholder.log', 'w')
        print >> log_file, sql_query
        print >> log_file, (variables,)
        print >> log_file, "------"
        # print sql_query % (variables,)
        log_file.close()
