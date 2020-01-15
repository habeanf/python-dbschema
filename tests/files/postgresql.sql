CREATE TABLE table1 (
  id serial primary key,
  val1 integer not null default 12,
  val2 varchar(50)
);
COMMENT ON TABLE table1 IS 'Comment for table1';

CREATE TABLE table2 (
  id serial primary key,
  val3 integer,
  ref_table1 integer references table1
);
COMMENT ON TABLE table2 IS 'Table2 with reference to table1';

CREATE VIEW view1 AS SELECT id, val2 FROM table1;
COMMENT ON VIEW view1 IS 'Comment for view1';
