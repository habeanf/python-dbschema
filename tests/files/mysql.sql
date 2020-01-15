CREATE TABLE table1 (
  id integer primary key auto_increment,
  val1 integer not null default 12,
  val2 varchar(50)
) COMMENT 'Comment for table1';

CREATE TABLE table2 (
  id integer primary key auto_increment,
  val3 integer,
  ref_table1 integer,
  FOREIGN KEY (ref_table1) REFERENCES table1(id)
) comment 'Table2 with reference to table1';

CREATE VIEW view1 AS SELECT id, val2 FROM table1;
