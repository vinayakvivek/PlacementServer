drop table if exists eligibility;
drop table if exists jaf;
drop table if exists time_slot;
drop table if exists resume;
drop table if exists company;
drop table if exists ic;
drop table if exists student;
drop table if exists department;


drop sequence if exists time_slot_id;
drop sequence if exists dept_id;
drop sequence if exists ic_id;
drop sequence if exists company_id;


create sequence if not exists time_slot_id start 1;
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
);

CREATE TABLE time_slot(
  id INT PRIMARY KEY DEFAULT nextval('time_slot_id'),
  start_time timestamp,
  end_time timestamp
);

CREATE TABLE jaf(
  company_id INT,
  jaf_no INT,
  name VARCHAR(20),
  description VARCHAR(80),
  stipend INT,
  cpi_cutoff NUMERIC(4,2),
  interview_slot_id INT,
  alloted_ic_id  INT,
  PRIMARY KEY(company_id,jaf_no),
  FOREIGN KEY (company_id) references company(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (interview_slot_id) references time_slot(id),
  FOREIGN KEY (alloted_ic_id) references ic(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE eligibility(
    company_id INT,
    jaf_no INT,
    dept_id INT,
    PRIMARY KEY (company_id,jaf_no,dept_id),
    FOREIGN KEY (company_id, jaf_no) references jaf(company_id,jaf_no)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (dept_id) references department(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


