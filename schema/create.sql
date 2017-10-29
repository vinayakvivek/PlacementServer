drop table if exists company;
drop table if exists ic;
drop table if exists student;
drop table if exists department;

drop sequence if exists dept_id;
drop sequence if exists ic_id;
drop sequence if exists company_id;

create sequence if not exists dept_id start 1;
create sequence if not exists ic_id start 1;
create sequence if not exists company_id start 1;


CREATE TABLE department(
  id  int primary key default nextval('dept_id'),
  name VARCHAR(30)
);

CREATE TABLE student(
  rollno  VARCHAR(10),
  name    VARCHAR(30),
  cpi     numeric(4,2),
  dept_id int,
  PRIMARY KEY(rollno),
  FOREIGN KEY (dept_id) references department(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  password VARCHAR(20)
);

CREATE TABLE ic(
  id  int primary key default nextval('ic_id'),
  rollno VARCHAR(10),
  FOREIGN KEY (rollno) references student(rollno)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  password VARCHAR(20)
);

CREATE TABLE company(
  id  int primary key default nextval('company_id'),
  name VARCHAR(30),
  email VARCHAR(30) unique,
  password VARCHAR(20)
);

