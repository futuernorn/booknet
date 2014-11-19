"""
EasyPG - a module to make it easier to connect to PostgreSQL with different configurations.

:version: 8
"""

import os.path
from contextlib import closing, contextmanager
import psycopg2
from ConfigParser import SafeConfigParser

config_name = 'pgapp'

def connect(context=True, autocommit=True, cfgname=None, **kwargs):
    """
    Connects to the database.  Configuration is read from the configuration
    file ``pgapp.cfg``, if available.

    :param context: whether to wrap the connection in an auto-closing context manager.
    :param kwargs: Default configuration parameters.
    :param cfgname: The base name of the configuration file.  The file ``<cfgname>.cfg``
                    is read.  If unspecified, the module variable ``config_name`` is used.
    :return: The database connection, wrapped in a context manager for a ``with`` block.
    :rtype: psycopg2.Connection
    """
    cp = SafeConfigParser()
    if cfgname is None:
        cfgname = config_name
    cfg_fn = cfgname + '.cfg'
    if not os.path.exists(cfg_fn):
        raise IOError('config file %s does not exist' % (cfg_fn,))
    cp.read('%s.cfg' % (cfgname,))
    opts = dict(kwargs.items())
    opts.update(cp.items('database'))
    cxn = psycopg2.connect(**opts)
    cxn.autocommit = autocommit
    if context:
        return closing(cxn)
    else:
        return cxn

@contextmanager
def cursor(**kwargs):
    """
    Context-managed cursor and database connection.  This will yield a cursor,
    and close both the cursor and the database connection.
    :param kwargs: The connection arguments.
    :return:
    """
    dbc = connect(context=False, **kwargs)
    try:
        cur = dbc.cursor()
        try:
            yield cur
        finally:
            dbc.close()
    finally:
        dbc.close()

def demo():
    import sys
    global config_name
    if sys.argv[1:]:
        config_name = sys.argv[1]
    with cursor() as cur:
        print "connected to database"
        cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
        for (tbl,) in cur:
            print "table: %s" % (tbl,)

if __name__ == '__main__':
    demo()
