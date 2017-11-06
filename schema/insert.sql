insert into department values(nextval('dept_id'),'CSE');
insert into department values(nextval('dept_id'),'Elec');
insert into department values(nextval('dept_id'),'Aero');
insert into department values(nextval('dept_id'),'Chemical');
insert into department values(nextval('dept_id'),'EP');
insert into department values(nextval('dept_id'),'Meta');
insert into department values(nextval('dept_id'),'HS');

insert into student values('1','messi',9.82,1,'user1');
insert into student values('2','suarez',9.00,2,'user2');
insert into student values('3','dembele',8.12,3,'user3');
insert into student values('4','iniesta',9.84,4,'user4');
insert into student values('5','sergio',9.10,5,'user5');
insert into student values('6','xavi',9.40,3,'user6');

insert into ic values(nextval('ic_id'),'1','ic1');
insert into ic values(nextval('ic_id'),'2','ic2');
insert into ic values(nextval('ic_id'),'3','ic3');

insert into company values(nextval('company_id'),'Rakuten','rak@gmail.com','company1');
insert into company values(nextval('company_id'),'Emirates','emi@gmail.com','company2');
insert into company values(nextval('company_id'),'Qatar','qat@gmail.com','company3');
insert into company values(nextval('company_id'),'samsung','sam@gmail.com','company4');
insert into company values(nextval('company_id'),'apple','app@gmail.com','company5');

insert into time_slot values(nextval('time_slot_id'),TIMESTAMP '2011-05-16 15:36:38', TIMESTAMP '2011-05-16 20:36:38');

insert into jaf values(1,1,'TestJaf1','Intern',10000,9.00,1,1);
insert into jaf values(2,2,'TestJaf2','Intern',10000,8.00,1,2);
insert into jaf values(3,1,'TestJaf3','Intern',10000,7.00,1,3);
insert into jaf values(4,1,'TestJaf4','Intern',10000,6.00,1,1);
insert into jaf values(1,2,'TestJaf5','Intern',10000,8.50,1,1);

insert into eligibility values(1,1,1);
insert into eligibility values(1,1,2);
insert into eligibility values(2,2,1);
insert into eligibility values(3,1,2);

insert into signedjafs(rollno,company_id,jaf_no) values('1',1, 1);
insert into signedjafs(rollno,company_id,jaf_no) values('1',2, 2);
