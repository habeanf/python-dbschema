Fixed version from https://bitbucket.org/andialbrecht/python-dbschema

python-dbschema
===============

``dbschema`` is a Python module to inspect database schema
definitions.


Installation
------------

The module can be installed from the `Python Package Index
<http://pypi.python.org/pypi/dbschema>`_ for example by running::

  pip install dbschema

The module is compatible with Python 2.7, >=3.2 and PyPy. Depending on
the database system you want to access a DB-API2 (:pep:`249`)
compliant driver is required.


Usage
-----

The following example shows the basic usage of the ``dbschema``
module:

.. sourcecode:: pycon

   >>> import dbschema
   >>> import psycopg2  # in this example we're using a PostgreSQL database
   >>> connection = psycopg2.connect(dbname='demo', user='john', password='doe')
   >>> schema = dbschema.open('postgresql', connection)
   >>> tables = schema.get_tables()
   >>> for table in schema.get_tables():
   ...     print(table.name)
   ...
   artist
   track
   artist_track_rel
   […]
   >>> 

Continue with the `tutorial
<https://python-dbschema.readthedocs.org/en/latest/tutorial.html>`_ to
learn more about the database object.


License
-------

dbschema is licensed under the BSD license.


Resources
---------

Documentation
  http://python-dbschema.readthedocs.org/en/latest/

Bug tracker
  https://bitbucket.org/andialbrecht/python-dbschema/issues

Source code
  https://bitbucket.org/andialbrecht/python-dbschema
