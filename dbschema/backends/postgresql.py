# -*- coding: utf-8 -*-

from .. import objects
from .base import BaseDatabase


class Database(BaseDatabase):
    dbapi_module = 'psycopg2'
    structure = (
        (objects.Namespace, (
            (objects.Table, (
                (objects.Column, None),
                (objects.ForeignKey, None),
            )),
            (objects.View, (
                (objects.Column, None),
            )),
        )),
    )

    def get_server_info(self):
        result = list(self.run_query('select version()'))[0]
        return result['version']

    def _initialize(self):
        nsp_map = {}
        for item in self.run_query(PG_INITIAL_SQL):
            if item['nspoid'] is not None:
                if item['nspoid'] not in nsp_map:
                    nsp = objects.Namespace(
                        item['nspname'], oid=item['nspoid'])
                    self.add_child(nsp)
                    nsp_map[item['nspoid']] = nsp
                else:
                    nsp = nsp_map[item['nspoid']]
            else:
                nsp = None
            if item['objtype'] == 'table':
                nsp.add_child(objects.Table(
                    item['relname'], description=item['description'],
                    oid=item['reloid']))
            elif item['objtype'] == 'view':
                nsp.add_child(objects.View(
                    item['relname'], description=item['description'],
                    oid=item['reloid']))
        self.set_dirty(objects.Namespace, False)
        self.set_dirty(objects.Table, False)
        self.set_dirty(objects.View, False)

    def get_default_namespace(self):
        search_path = list(
            self.run_query('show search_path'))[0]['search_path']
        for path in search_path.split(','):
            if path == '"$user"':
                path = list(self.run_query('select current_user'))[0]['current_user']
            nsp = self.find_exact(type_cls=objects.Namespace, name=path)
            if nsp is not None:
                return nsp

    def refresh_types(self, type_clss):
        if objects.Column in type_clss:
            self._refresh_columns()
        if objects.ForeignKey in type_clss:
            self._refresh_constraints()

    def _refresh_constraints(self):
        # TODO(andi) Only FK constraints are currently recognized
        sql = ("select con.oid, con.contype, con.conname,"
               " con.conrelid, con.confrelid, dsc.description"
               " from pg_constraint con"
               " left join pg_description dsc on dsc.objoid = con.oid")
        for item in self.run_query(sql):
            if item['contype'] == 'f':
                ftable = self.db.find_by_oid(item['confrelid'])
                table = self.db.find_by_oid(item['conrelid'])
                table.add_child(objects.ForeignKey(
                    item['conname'], description=item['description'],
                    oid=item['oid'], foreign_table=ftable))

    def _refresh_columns(self):
        # TODO(andi) columns for relkind 'i' and 'S' still missing
        sql = ("select att.attrelid, att.attnum, att.attname, dsc.description"
               " from pg_attribute att"
               " join pg_class rel on rel.oid = att.attrelid "
               "   and rel.relkind in ('r', 'v')"
               " left join pg_description dsc on dsc.objoid = att.attrelid"
               "  and dsc.objsubid = att.attnum"
               " where att.attnum >= 1")
        for item in self.run_query(sql):
            obj = self.db.find_by_oid(item['attrelid'])
            if obj is None:
                print(item)
            obj.add_child(objects.Column(
                item['attname'], description=item['description'],
                oid='%s-%s' % (obj.oid, item['attname'])))


PG_INITIAL_SQL = """
SELECT nsp.oid AS nspoid,
       nsp.nspname,
       rel.oid AS reloid,
       rel.relname,
       des.description,
       CASE
           WHEN rel.relkind = 'r' THEN 'table'
           WHEN rel.relkind = 'i' THEN 'index'
           WHEN rel.relkind = 'S' THEN 'sequence'
           WHEN rel.relkind = 'v' THEN 'view'
           -- somehow this is required, otherwise the above fails
           ELSE rel.relkind::char

       END AS objtype --        rel.*

FROM pg_class rel
LEFT JOIN pg_description des ON des.objoid = rel.oid
AND des.objsubid = 0
LEFT JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE rel.relkind IN ('v',
                      'r',
                      'S')
UNION -- languages

SELECT NULL,
       NULL,
       lan.oid,
       lan.lanname,
       des.description,
       'language'
FROM pg_language lan
LEFT JOIN pg_description des ON des.objoid = lan.oid
UNION -- users

SELECT NULL,
       NULL,
       use.usesysid,
       use.usename,
       NULL,
       'user'
FROM pg_user use
UNION -- functions

SELECT nsp.oid,
       nsp.nspname,
       pro.oid,
       pro.proname,
       des.description,
       'function'
FROM pg_proc pro
LEFT JOIN pg_namespace nsp ON nsp.oid = pro.pronamespace
LEFT JOIN pg_description des ON des.objoid = pro.oid
"""
