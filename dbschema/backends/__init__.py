# -*- coding: utf-8 -*-

import importlib

from ..exceptions import DBSchemaError


_BACKENDS = {
    'mysql': None,
    'postgresql': None,
    'sqlite3': None,
}

#: Identifiers for known backends.
BACKEND_NAMES = list(_BACKENDS)


def get_backend(name):
    """Returns a backend implementation by name.

    :param name: Backend name, must be one of :const:`BACKEND_NAMES`.
    :returns: Backend class
    :raises: DBSchemaError if a invalid backend was requested.
    """
    if name in _BACKENDS:
        klass = _BACKENDS[name]
        if klass is None:
            try:
                mod = importlib.import_module('dbschema.backends.%s' % name)
                klass = getattr(mod, 'Database')
            except (ImportError, AttributeError) as exc:
                raise DBSchemaError(
                    'Failed to load backend %r: %s' % (name, exc))
            _BACKENDS[name] = klass
        return klass
    raise DBSchemaError('Unknown backend %r' % name)
