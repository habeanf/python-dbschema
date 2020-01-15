# -*- coding: utf-8 -*-

import logging

from ..objects import Database


logger = logging.getLogger('dbschema')


class BaseDatabase(Database):

    def __init__(self, name, log_sql=False):
        super(BaseDatabase, self).__init__(name)
        self._log_sql = log_sql

    def get_cursor(self):
        """Returns a new DB-API2 cursor."""
        return self.connection.cursor()

    def run_query(self, sql, params=None):
        """Runs a database query and yields results as dicts."""
        cur = self.get_cursor()
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        if self._log_sql:  # NOQA
            logger.info('SQL: %s [%r]', sql, params)
        if not cur.description:
            # SQLite3 doesn't have a description when no rows are
            # returned. Error out here.
            raise StopIteration
        names = [c[0] for c in cur.description]
        for row in cur.fetchall():
            yield dict(zip(names, row))
