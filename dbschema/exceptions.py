class DBSchemaError(Exception):
    """Base class for all exceptions in this module."""


class DBSchemaOperationError(DBSchemaError):
    """Used when a database operation fails.

    :ivar orignal_exc: Contains the original exception raised by the
      underlying DB-API2 module.
    """
    original_exc = None
