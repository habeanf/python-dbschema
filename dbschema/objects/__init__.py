# -*- coding: utf-8 -*-

import importlib

from ..exceptions import DBSchemaError


DOESNOTEXIST = object()


class Node(object):
    """Base class for database objects."""

    def __init__(self, name, **kwargs):
        """Constructor."""
        # TODO(andi) maybe it's more efficient to store children in a
        # dict (oid -> object)? It would improve oid lookups and it
        # would be much easier to replace a child object.
        self.children = set([])
        self.parent = None
        self.name = name  #: The name of the object.
        self.description = None  #: The description of the object.
        self.oid = None  #: A unique identifier provided by the underlying backend.
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return '<%s:%s.%s at 0x%0x>' % (self.__class__.__name__,
                                        self.parent.name or '??',
                                        self.name or '??', id(self))

    def __hash__(self):
        return hash((self.__class__, self.parent, self.name))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __lt__(self, other):
        return self.name < other.name

    def _print_tree(self, level=0):  # NOQA
        # use for debugging, prints the tree
        print('%s%r' % ('  ' * level, self))
        for child in self.children:
            child._print_tree(level + 1)

    @property
    def db(self):
        if isinstance(self, Database):
            return self
        return self.parent.db

    def add_child(self, obj):
        """Adds a child objects."""
        obj.parent = self
        if obj not in self.children:
            self.children.add(obj)
        # TODO(andi): This assumes that the node is already child of a root
        # Database node which makes it impossible to create a sub-tree that
        # should be added to the real root later. For example:
        # db = Database()
        # node = Node()
        # db.add_child(node)
        # sub = Node()
        # sub.add_child(Node())  # <-- fails
        # node.add_child(db)
        self.db._oid_idx[obj.oid] = obj
        return obj

    def find(self, type_cls=None, name=None, parent=None,
             recurse=True, **kwargs):
        """Yields database objects matching search parameters.

        All search parameters are optional. If not parameters are
        given all database objects are returned.

        :param type_cls: Find specific types.
        :type type_cls: Subclass of :class:`Node`
        :param name: The name to match.
        :type name: str
        :param parent: The parent of the objects that should be yieled.
        :type parent: Instance of :class:`Node`
        :param kwargs: All other keyword parameters are used to
          compare with the attributes of the child instances.
        :param recurse: If ``True`` (the default) recurse into children.

        :returns: Iterator of :class:`Node` instances.
        """
        for child in self.children:
            yield_child = True
            if type_cls is not None and not isinstance(child, type_cls):
                yield_child = False
            if name is not None and child.name != name:
                yield_child = False
            if parent is not None and child.parent != parent:
                yield_child = False
            for key in kwargs:
                child_value = getattr(child, key, DOESNOTEXIST)
                if child_value == DOESNOTEXIST or child_value != kwargs[key]:
                    yield_child = False
                    break
            if yield_child:
                yield child
            if recurse:
                # yield from FTW! But we want to support older Python
                # versions too...
                for cchild in child.find(type_cls=type_cls, name=name,
                                         parent=parent, recurse=recurse,
                                         **kwargs):
                    yield cchild

    def find_exact(self, **kwargs):
        """Returns exact one match or None.

        For parameter reference see :func:`find`.
        """
        results = list(self.find(**kwargs))
        if len(results) == 1:
            return results[0]
        return None

    def get_child_types(self):
        """Returns a set of child types for this node."""
        types = set()
        for child in self.children:
            types.add(child.__class__)
        return types


class Database(Node):
    """Central database class."""

    dbapi_module = None
    structure = []

    def __init__(self, name):
        super(Database, self).__init__(name)
        self._conn = None
        self._conn_kwargs = None
        self._oid_idx = {}
        self._dirty = set()
        for type_cls, children in self.structure:
            self._populate_dirty(type_cls, children)

    def _populate_dirty(self, type_cls, children):
        self._dirty.add(type_cls)
        children = children or []
        for type_cls, cchildren in children:
            self._populate_dirty(type_cls, cchildren)

    def set_connection(self, connection, **connect_kwargs):
        """Sets the connection to interact with the database.

        :param connection: If not ``None``, a already opened database
          connection.  :type connection: DB-API2 connection or None
        :param connect_kwargs: Connection kwargs if not connection
          is given.

        It is an error if both ``connection`` and ``connect_kwargs`` are
        given.
        """
        if connection and connect_kwargs:
            raise DBSchemaError(
                'Either connection or connect_kwargs is allowed, not both.')
        elif connection:
            self._conn = connection
            self._conn_kwargs = None
        else:
            self._conn = None
            self._conn_kwargs = connect_kwargs

    @property
    def dbapi(self):
        try:
            dbapi = importlib.import_module(self.dbapi_module)
        except ImportError as err:
            raise DBSchemaError(
                'Failed to load database module: %s' % err)
        return dbapi

    @property
    def connection(self):
        if self._conn is None:
            try:
                self._conn = self.dbapi.connect(**self._conn_kwargs)
            except Exception as err:
                raise DBSchemaError(
                    'Could not connect to database: %s' % err)
        return self._conn

    def _initialize(self):
        """Initializes database objects.

        This method is called after the creation of a
        :class:`Database` instance. It's purpose is to pre-populate
        the tree of database objects. Backends don't need to implement
        this method, but if they do it should perform a quick
        operation to fetch basic information about the database.
        """
        pass

    def find_by_oid(self, oid):
        return self._oid_idx.get(oid, None)

    def get_server_info(self):
        """Returns version information of the database.

        :rtype: str
        """
        raise NotImplementedError('Database.get_version()')

    def get_default_namespace(self):
        """Returns the default namespace or None.

        :rtype: :class:`Namespace` or ``None``
        """
        return None

    def _get_types_from_default_ns(self, type_cls):
        """Helper to yield objects from default namespace."""
        self._refresh_types_internal([type_cls])
        nsp = self.get_default_namespace() or self
        return nsp.find(type_cls=type_cls)

    def get_tables(self):
        """Yields all tables from default namespace.

        :rtype: Generator of :class:`Table` instances.
        """
        return self._get_types_from_default_ns(Table)

    def get_views(self):
        """Yields all views from the default namespace.

        :rtype: Generator of :class:`View` instances-
        """
        return self._get_types_from_default_ns(View)

    # def refresh(self, obj, type_cls=None):
    #     """Updates obj.

    #     If type_cls is given, the given object is requested to be
    #     updated in regard to the given type_cls. For example, if obj
    #     is a table and type_cls :class:`Column` then this function
    #     should populate the columns for obj.

    #     :param type_cls: A :class:`Node` subclass.
    #     """
    #     pass

    def set_dirty(self, type_cls, dirty):
        """Marks/unmarks a certain type as dirty.

        :param type_cls: A :class:`Node` subclass.
        :param dirty: Wether the type is dirty.
        :type dirty: bool
        """
        if dirty and type_cls not in self._dirty:
            self._dirty.add(type_cls)
        elif not dirty and type_cls in self._dirty:
            self._dirty.remove(type_cls)

    def refresh_types(self, type_clss):
        """Instructs the backend to refresh certain types.

        "type_clss" is a list of :class:`dbschema.objects.Node`
        classes that should be refreshed.
        """
        pass

    def _refresh_types_internal(self, type_clss):
        tbd = set(type_clss).intersection(self._dirty)
        if not tbd:
            return
        self._dirty = self._dirty.difference(tbd)
        self.refresh_types(tbd)


class Namespace(Node):
    """A namespace/schema in the database."""

    def is_default_namespace(self):
        """Returns True if this namespace is a default namespace."""
        return self.db.get_default_namespace() == self


class Table(Node):
    """A table in the database."""

    def get_columns(self):
        """Yields columns of this table.

        :rtype: Generator of :class:`Column` instances.
        """
        self.db._refresh_types_internal([Column])
        return self.find(type_cls=Column)

    def get_foreign_keys(self):
        """Yields foreign key definitions.

        :rtype: Generator of :class:`ForeignKey` instances.
        """
        self.db._refresh_types_internal([ForeignKey])
        return self.find(type_cls=ForeignKey)

    def get_reverse_foreign_keys(self):
        """Yields foreign keys pointing to this table.

        :rtype: Generaotr of :class:`ForeignKey` instances.
        """
        self.db._refresh_types_internal([ForeignKey])
        return self.db.find(type_cls=ForeignKey, foreign_table=self)


class View(Node):
    """A view in the database."""

    def get_columns(self):
        """Yields columns of this view."""
        self.db._refresh_types_internal([Column])
        return self.find(type_cls=Column)


class Column(Node):
    """A column of a view or table."""


class ForeignKey(Node):
    """A foreign key definition of a table."""

    def __init__(self, *args, **kwargs):
        self.foreign_table = None
        super(ForeignKey, self).__init__(*args, **kwargs)

    def get_foreign_table(self):
        return self.foreign_table
