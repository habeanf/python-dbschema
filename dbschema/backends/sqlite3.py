# -*- coding: utf-8 -*-

from itertools import chain

from .. import objects
from .base import BaseDatabase


class Database(BaseDatabase):
    dbapi_module = 'sqlite3'
    structure = (
        (objects.Table, (
            (objects.Column, None),
            (objects.ForeignKey, None),
        )),
        (objects.View, (
            (objects.Column, None),
        )),
    )

    def get_server_info(self):
        return 'SQLite %s' % self.dbapi.sqlite_version

    def _initialize(self):
        sql = 'select type, name, tbl_name, sql from sqlite_master'
        for item in self.run_query(sql):
            if item['type'] == 'table':
                klass = objects.Table
            elif item['type'] == 'view':
                klass = objects.View
            else:
                continue
            self.add_child(
                klass(item['name'], createstatement=item['sql'],
                      oid=item['name']))
        self.db.set_dirty(objects.Table, False)
        self.db.set_dirty(objects.View, False)

    def refresh_types(self, type_clss):
        if objects.Column in type_clss:
            self._refresh_columns()
        if objects.ForeignKey in type_clss:
            self._refresh_foreign_keys()

    def _refresh_columns(self):
        for obj in chain(self.find(type_cls=objects.Table),
                         self.find(type_cls=objects.View)):
            # parameter substitution does not work for pragma statements.
            for item in self.run_query('pragma table_info(%s)' % obj.name):
                obj.add_child(objects.Column(
                    item['name'], oid='%s.%s' % (obj.oid, item['cid'])))

    def _refresh_foreign_keys(self):
        for obj in self.find(type_cls=objects.Table):
            for item in self.run_query(
                    'pragma foreign_key_list(%s)' % obj.name):
                ftable = self.db.find_by_oid(item['table'])
                obj.add_child(objects.ForeignKey(
                    name='%s.%s' % (obj.name, item['from']),
                    oid='%s.%s' % (obj.name, item['from'] ),
                    foreign_table=ftable))
