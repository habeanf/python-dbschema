import sys
try:
    from configparser import ConfigParser, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError
from collections import namedtuple
from os.path import abspath, join, dirname

import sqlparse


BackendConfig = namedtuple('BackendConfig', 'name kwargs')
conf = None
HERE = abspath(dirname(__file__))


def _get_config():
    global conf
    if conf is None:
        conf = ConfigParser()
        conf.read(join(HERE, 'databases.conf'))
    return conf

_dbs = []
def _get_dbs(config, backends):
    global _dbs
    if _dbs:
        return _dbs
    import dbschema
    _dbs = []
    test_db_name = 'dbschema_test'
    for b in backends:
        if b.name == 'postgresql':
            kwargs = b.kwargs.copy()
            kwargs['dbname'] = 'template1'
            import psycopg2
            conn = psycopg2.connect(**kwargs)
            conn.set_isolation_level(0)
            cur = conn.cursor()
            cur.execute('DROP DATABASE IF EXISTS %s;' % test_db_name)
            cur.execute('CREATE DATABASE %s;' % test_db_name)
            conn.close()
        elif b.name == 'mysql':
            kwargs = b.kwargs.copy()
            kwargs['db'] = 'mysql'
            import MySQLdb
            conn = MySQLdb.connect(**kwargs)
            cur = conn.cursor()
            cur.execute('DROP DATABASE IF EXISTS %s;' % test_db_name)
            cur.execute('CREATE DATABASE %s;' % test_db_name)
            conn.close()
        structure = open(join(HERE, 'files', '%s.sql' % b.name)).read()
        try:
            db = dbschema.open(b.name, **b.kwargs)
            cur = db.get_cursor()
        except dbschema.exceptions.DBSchemaError as exc:
            sys.stderr.write('%s\n' % exc)
            continue
        structure = structure % {
            'test_db_name': test_db_name,
        }
        for statement in sqlparse.split(structure):
            if not statement.strip():
                continue
            cur.execute(statement)
        cur.close()
        db.connection.commit()
        if not b.name == 'sqlite3':
            db.connection.close()
        db = dbschema.open(b.name, **b.kwargs)
        _dbs.append(db)
    return _dbs


def pytest_generate_tests(metafunc):
    config = _get_config()
    import sqlite3
    conn = sqlite3.connect(':memory:')
    backends = [BackendConfig('sqlite3', {'connection': conn})]
    for backend_name in config.sections():
        if backend_name == 'postgresql':
            try:
                import psycopg2
            except ImportError:
                continue
        elif backend_name == 'mysql':
            try:
                import MySQLdb
            except ImportError:
                continue
        kwargs = {o: config.get(backend_name, o)
                  for o in config.options(backend_name)}
        backends.append(BackendConfig(backend_name, kwargs))
    if 'backend' in metafunc.fixturenames:
        metafunc.parametrize('backend', backends,
                             ids=[b.name for b in backends])
    if 'db' in metafunc.fixturenames:
        dbs = _get_dbs(config, backends)
        metafunc.parametrize('db', dbs, ids=[b.name for b in backends])
