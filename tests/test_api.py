"""API tests."""

import pytest

import dbschema

try:
    basestring
except NameError:  # py3
    basestring = str

# dbschema.open


def test_open(backend):
    db = dbschema.open(backend.name, **backend.kwargs)
    assert isinstance(db, dbschema.objects.Database)


def test_open_invalid_backend():
    with pytest.raises(dbschema.exceptions.DBSchemaError):
        dbschema.open('foo')


def test_open_connection_or_kwargs():
    sqlite3 = pytest.importorskip('sqlite3')
    conn = sqlite3.connect(':memory:')
    kwargs = {'database': ':memory:'}
    with pytest.raises(dbschema.exceptions.DBSchemaError):
        dbschema.open(dbschema.BACKEND_SQLITE3, conn, **kwargs)
    dbschema.open(dbschema.BACKEND_SQLITE3, conn)
    dbschema.open(dbschema.BACKEND_SQLITE3, **kwargs)


# dbschema.objects.Node

def test_nodes_sort_by_name():
    t1 = dbschema.objects.Table(name='foo')
    t2 = dbschema.objects.Table(name='bar')
    v1 = dbschema.objects.View(name='baz')
    assert sorted([v1, t2, t1]) == [t2, v1, t1]


def test_get_child_types():
    db = dbschema.objects.Database(name="test")
    node = dbschema.objects.Node(name="foo")
    db.add_child(node)
    assert node.get_child_types() == set()
    t1 = dbschema.objects.Table(name="bar")
    node.add_child(t1)
    t1.add_child(dbschema.objects.Column(name="col"))
    node.add_child(dbschema.objects.View(name="baz"))
    assert node.get_child_types() == set([dbschema.objects.Table,
                                          dbschema.objects.View])
    assert t1.get_child_types() == set([dbschema.objects.Column])


# dbschema.objects.Database

def test_db_get_server_info(db):
    info = db.get_server_info()
    assert isinstance(info, basestring)


def test_get_tables(db):
    assert set([t.name for t in db.get_tables()]) == set(['table1', 'table2'])


def test_get_views(db):
    assert [t.name for t in db.get_views()] == ['view1']


# dbschema.objects.Namespace
def test_namespace_is_default(db):
    ns = db.get_default_namespace()
    if ns is not None:  # backend has no namespaces
        assert ns.is_default_namespace()


# dbschema.objects.Table

class TestTable:

    def test_table_get_columns(self, db):
        t = db.find_exact(type_cls=dbschema.objects.Table, name='table1')
        assert t is not None
        assert sorted(c.name for c in t.get_columns()) == ['id', 'val1', 'val2']

    def test_get_foreignkeys(self, db):
        t = db.find_exact(type_cls=dbschema.objects.Table, name='table2')
        assert t is not None
        fks = list(t.get_foreign_keys())
        assert len(fks) == 1
        assert fks[0].foreign_table.name == 'table1'

    def test_get_reverse_foreignkeys(self, db):
        t = db.find_exact(type_cls=dbschema.objects.Table, name='table1')
        assert t is not None
        fks = list(t.get_reverse_foreign_keys())
        assert len(fks) == 1
        assert fks[0].parent.name == 'table2'


# dbschema.objects.View


def test_view_get_columns(db):
    v = db.find_exact(type_cls=dbschema.objects.View, name='view1')
    assert v is not None
    assert sorted(c.name for c in v.get_columns()) == ['id', 'val2']


# dbschema.objects.ForeignKey

def test_fk_get_foreing_table(db):
    t1 = db.find_exact(type_cls=dbschema.objects.Table, name='table1')
    t2 = db.find_exact(type_cls=dbschema.objects.Table, name='table2')
    assert t2 is not None
    fk = list(t2.get_foreign_keys())[0]
    assert fk.get_foreign_table() == t1
