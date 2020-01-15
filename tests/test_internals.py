import pytest

import dbschema


def test_get_backend_fails_on_broken_backend():
    dbschema.backends._BACKENDS['invalid'] = None
    try:
        with pytest.raises(dbschema.exceptions.DBSchemaError):
            dbschema.backends.get_backend('invalid')
    finally:
        del dbschema.backends._BACKENDS['invalid']
