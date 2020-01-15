# -*- coding: utf-8 -*-

from .. import objects
from .base import BaseDatabase


class Database(BaseDatabase):
    dbapi_module = 'MySQLdb'
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
        return 'MySQL %s' % self.connection.get_server_info()

    def _initialize(self):
        nsp_map = {}
        for item in self.run_query(INITIAL_SQL):
            if item['TYPE'] == 'schema':
                if item['id'] in nsp_map:
                    nsp = nsp_map[item['id']]
                else:
                    nsp = objects.Namespace(item['name'], oid=item['id'])
                    self.add_child(nsp)
                    nsp_map[item['id']] = nsp
            elif item['TYPE'] in ('SYSTEM VIEW', 'VIEW'):
                nsp = nsp_map[item['parent']]
                nsp.add_child(objects.View(
                    item['name'], description=item['description'],
                    oid=item['id']))
            elif item['TYPE'] == 'BASE TABLE':
                nsp = nsp_map[item['parent']]
                nsp.add_child(objects.Table(
                    item['name'], description=item['description'],
                    oid=item['id']))
            elif item['TYPE'] == 'column':
                table = self.find_by_oid(item['parent'])
                if table is None:
                    continue
                table.add_child(objects.Column(
                    item['name'], description=item['description'],
                    oid=item['id']))
        self.db.set_dirty(objects.Table, False)
        self.db.set_dirty(objects.View, False)
        self.db.set_dirty(objects.Column, False)

    def get_default_namespace(self):
        default = list(self.run_query('select database();'))[0]['database()']
        if default is not None:
            return self.find_exact(type_cls=objects.Namespace, oid=default)

    def refresh(self, obj, type_cls):
        if type_cls == objects.ForeignKey:
            self._refresh_constraints(obj)

    def refresh_types(self, type_clss):
        if objects.ForeignKey in type_clss:
            self._refresh_constraints()

    def _refresh_constraints(self):
        for item in self.run_query(SQL_FKS):
            table = self.db.find_by_oid(item['tableoid'])
            ftable = self.db.find_by_oid(item['refoid'])
            table.add_child(objects.ForeignKey(
                item['constraint_name'], oid=item['oid'],
                foreign_table=ftable))


INITIAL_SQL = """
SELECT *
FROM
  (SELECT lower(SCHEMA_NAME) AS id,
          SCHEMA_NAME AS name,
          NULL AS description,
          'schema' AS TYPE,
          NULL AS parent,
          0 AS pos
   FROM information_schema.schemata
   UNION SELECT lower(concat(table_schema, '.', TABLE_NAME)) AS id,
                TABLE_NAME AS name,
                table_comment AS description,
                table_type AS TYPE,
                lower(table_schema) AS parent,
                1 AS pos
   FROM information_schema.tables
   UNION SELECT lower(concat(table_schema, '.', TABLE_NAME, '.', COLUMN_NAME)) AS id,
                COLUMN_NAME AS name,
                column_comment AS description,
                'column' AS TYPE,
                lower(concat(table_schema, '.', TABLE_NAME)) AS parent,
                3 AS pos
   FROM information_schema.columns) x
ORDER BY pos ASC
"""

SQL_FKS = """
SELECT concat(tc.constraint_schema, '.', tc.constraint_name) AS oid,
       tc.constraint_type, tc.constraint_name,
       concat(tc.table_schema, '.', tc.table_name) AS tableoid,
       group_concat(kc.column_name, ',') AS columns,
       concat(kc.referenced_table_schema, '.', kc.referenced_table_name) AS refoid,
       group_concat(kc.referenced_column_name, ',') AS refcolumns
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kc ON kc.constraint_schema = tc.constraint_schema
AND kc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
GROUP BY kc.column_name,
         kc.referenced_column_name;
"""
