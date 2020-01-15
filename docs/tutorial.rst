==========
 Tutorial
==========


Connection to a Database
========================

TODO

.. dbschema.open usage
.. how dbschema deals with connections (always assumes open)
.. set_connection
.. dependencies for various DBMS


Examining the Database Schema
=============================

TODO

.. quick access with the Database object
.. objects are stored hierachically
.. finding objects in hierarchy


Modifying the Database Schema
=============================

Example:

.. code-block:: pycon

   >>> import dbschema
   >>> op = dbschema.operation.SchemaOperation(dbschema.BACKEND_POSTGRESQL)
   >>> table = dbschema.objects.Table('foo')
   >>> op += table
   >>> table += dbschema.objects.Column('val1', int)
   >>> table += dbschema.objects.Column('val2', str, comment='val2 is a string value')
   >>> table.comment = 'An example table.'
   >>> print(op.as_sql())
   CREATE TABLE "foo" (
     val1 integer,
     val2 text
   );
   COMMENT ON TABLE "foo" IS 'An example table';
   COMMENT ON COLUMN "foo"."val2" IS 'val2 is a string value';
   >>> conn = psycopg2.connect(dbname='demo', user='john', password='doe')
   >>> op.backend.set_connection(conn)
   >>> op.execute()  # perform operation on database
   >>> 
