"""dbschema main module."""

__version__ = '0.1.0-dev'

from . import backends


# TODO(andi) Do we really need this constants here?  Maybe backends is
# a better place or alternatively backends should use them.
BACKEND_MYSQL = 'mysql'           #: Identifier for MySQL databases.
BACKEND_POSTGRESQL = 'postgresql' #: Identifier for PostgreSQL databases.
BACKEND_SQLITE3 = 'sqlite3'       #: Identifier for SQLite3 databases.


def open(backend, connection=None, log_sql=False, **connect_kwargs):
    """Returns a :class:`Schema` instance.

    :param backend: Backend identifier, must be one of
      :const:`dbschema.backends.BACKEND_NAMES`.
    :param connection: If not ``None``, a already opened database
      connection.
    :type connection: DB-API2 connection or None
    :param log_sql: If ``True`` SQL statements are logged (default: ``False``).
    :param connect_kwargs: Connection kwargs if not connection is
      given.

    It is an error if both ``connection`` and ``connect_kwargs`` are
    given.

    :returns: A :class:`Schema` instance.
    :raises: :exc:`dbschema.exceptions.DBSchemaError` if things went
      wrong.
    """
    db_cls = backends.get_backend(backend)
    db = db_cls(backend, log_sql=log_sql)
    db.set_connection(connection=connection, **connect_kwargs)
    db._initialize()
    return db
