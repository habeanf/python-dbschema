CREATE TABLE table1 (
  id integer primary key asc,
  val1 integer not null default 12,
  val2 text
);

CREATE TABLE table2 (
  id integer primary key asc,
  val3 integer,
  ref_table1 integer references table1
);

CREATE VIEW view1 AS SELECT id, val2 FROM table1;
