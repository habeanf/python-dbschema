=============
 Development
=============


Testing
=======

:mod:`dbschema` uses `py.test <pytest.org>`_ for testing. Since
:mod:`dbschema` works with various database backends a little setup is
required to run the full test suite. Without any additional setup
as explained below only tests for SQLite3 databases will be
executed.

For testing the ``sqlparse`` Python module is required.

Copy :file:`tests/databases.conf.example` to
:file:`tests/database.conf` and edit as needed. This configuration
file needs to be adapt to the database systems you've running on your
system and you need to set the parameters to access those databases
accordingly. Note that the database user needs permissions to create
and delete databases. Here's an example with PostgreSQL and MySQL
configured, and where all created databases created during the tests
are prefixed with ``dbschema_`` to avoid conflicts.

.. code-block:: ini

   [DEFAULT]
   db_prefix = dbschema_

   [postgresql]
   user = john
   password = foo

   [mysql]
   user = john
   password = foo
   host = localhost

If the file :file:`tests/database.conf` doesn't exist or is empty,
only the tests for SQLite databases will be run.

When ready, run :command:`py.test tests/` to run the tests using the
default Python interpreter.


Setting Up Databases for Testing
--------------------------------

As noted above each DBMS you want to test requires an entry in
:file:`test/databases.conf`. This section contains some notes on how
to set up various DBMS for testing on an Debian/Ubuntu system.

.. warning:: Security

   The following setups assume that you run distinct database
   instances for testing this module. Therefore all databases users
   created in this examples are superusers. Please don't use a
   production database for testing!


MySQL
~~~~~

First install the MySQL server and Python module with :command:`sudo
apt-get install mysql-server libmysqlclient-dev
python-mysqldb`\. During the installation you'll be prompted for a
password, note it down (or to be more secure, just remember it).

Next create a test user account. The test user needs privileges to
create and drop a database. If you don't care much about security for
this database installation just create a superuser with the following
commands:

.. code-block:: mysql

   $ mysql -u root -p
   mysql> CREATE USER 'test'@'localhost' IDENTIFIED BY 'secret';
   mysql> GRANT ALL PRIVILEGES ON *.* TO 'test'@'localhost';

Then in your :file:`tests/databases.conf` add

.. code-block:: ini

   [mysql]
   user = test
   password = secret
   host = localhost


Changelog
=========

.. include:: ../CHANGES
