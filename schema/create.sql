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
  id  INT PRIMARY KEY DEFAULT nextval('dept_id'),
  name VARCHAR(30)
);

CREATE TABLE student(
  rollno  VARCHAR(10),
  name    VARCHAR(30),
  cpi     NUMERIC(4,2),
  dept_id INT,
  PRIMARY KEY(rollno),
  FOREIGN KEY (dept_id) references department(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  password VARCHAR(20)
);

CREATE TABLE ic(
  id  INT PRIMARY KEY DEFAULT nextval('ic_id'),
  rollno VARCHAR(10),
  FOREIGN KEY (rollno) references student(rollno)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  password VARCHAR(20)
);

CREATE TABLE company(
  id  INT PRIMARY KEY DEFAULT nextval('company_id'),
  name VARCHAR(30),
  email VARCHAR(30) UNIQUE,
  password VARCHAR(20)
);

CREATE TABLE resume(
  rollno VARCHAR(10) PRIMARY KEY,
  resume_file BYTEA,
  verified_ic INT,
  FOREIGN KEY (rollno) references student(rollno)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (verified_ic) references ic(id)
)

