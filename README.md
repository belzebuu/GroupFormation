# Project Assignment


This repository contains the software to assign students to projects.
We assume given a set of project topics each with a subset of teams
available with bounded size, and a set of students with preferences on
the project topics. The task is to create teams of students to work on
the available project topics.



We assume that there is a local installation of
[Gurobi](http://www.gurobi.com) and that its module for python is in
the python path of the system.

In the following we describe how to define the input data and the work
flow.


- Original Data
- Transformed Data
- Workflow



## Original Data

We need two textual comma separeted files `projects.csv` and `students.csv`.

`projects.csv` contains data on the project topics, the number of teams
for each topic and the capacity of each group. Other information is
probably not relevant. 

The file has no header.  Each field is separeted by semicolumn
`;`. There is one line for each different team of a topic. Each line
contains the following fields:


- Topic identifier (eg, a number equal for all teams in the topic)
- Team identifier
- Title or topic
- Min capacity
- Max capacity
- Study Program: topics can be grouped in different study
                        programs to which students belong. Assignment of
                        students through programs is controlled by TODO. 
- Project identifier (a combination of topic and team identifier)
- Offering institute abbreviation
- Offering institute full name
- Need complementary short courses
- Working location


`students.csv` contains details on the students.

The file has no header. Each field is separeted by semicolumn `;`. There
is a line for each student enrolled. Each line contains the following
fields:

- Group identifier (different students may have the same group
  identifier if they enrolled together meaning that they want ot end in
  the same tems).
- Username 
- Study program
- Priority list (comma separated list of topic identifiers sorted in
decreasing order of preference)  
- Student identifier
- Studen full name 
- Email address
- Registration timestamp



`programs.csv`
		
The script `scripts/prepare-data.py` parses these files and generates
tjhe files used by the program.


## Transformed Data

Each instance consists of four files:
@<code>tmp_projects.txt@</code>
@<code>tmp_students.txt@</code>
@<code>tmp_priorities.txt@</code>
@<code>tmp_types.txt@</code>

Fields are separated by semicolon.

A further side constraint that is not discussed in the article must be
taken into account when solving the instances. Projects and students
belong to a type. In the instances available these types are
strings. The file tmp_types.txt specifies the compatibles types.

** File @<code>tmp_types.txt@</code>

The file contains information about the compatibility between student
and project types: For each student type, it provides the list of
acceptable project types.  The line starts with the student type. An
undefined number of acceptable project types follows.


#+BEGIN_EXAMPLE 
"biologi";"alle";"natbidat"
"farmaci";"alle";"farmaci"
"natbidat";"alle";"natbidat"
#+END_EXAMPLE



** File @<code>tmp_projects.txt@</code>

List of projects.  In each line:

- first field is an identifier of the topic
- second field an identifier for the team. The field is empty if only
  one team allowed
- fourth and fifth fields are the lower and upper bound of team
  size, respectively
- the sixth field is the area of the project.


#+BEGIN_EXAMPLE 
1;;3;5;nat501
2;;3;5;alle
3;;3;5;nat507
4;;4;5;alle
5;;3;5;alle
6;;3;5;alle
7;a;3;3;nat501
7;b;3;3;nat501
#+END_EXAMPLE


** File @<code>tmp_students.txt@</code>

List of students and groups. In each line:

- first field is the group identifier
- second field is the student id
- third field is the type of the student


#+BEGIN_EXAMPLE 
1;f721a356abf2d2a635fb5de74740e8ff;nat501
2;fbd97a97bd6426ca20b778f615b15378;nat501
4;57daeb7a328e3159c37654e32c0a73d0;nat501
5;f4466b5230902ceb1356a8ea42874aac;nat501
6;be10ca48a7ae7a3bbe7e877235244e37;nat501
7;7f2b3d0158e94656025d202aab952d66;nat501
8;ad783081894f2c65709b689571c9cb6c;nat501
9;72503179d2e1fc976c7e8f1aa489a9d1;nat501
10;4bf81f77fa048bfdc0eb60064a50e2f6;nat507
10;682f5f8b07d8b897d851e65848e2a67d;nat507
#+END_EXAMPLE


** File @<code>tmp_priorities.txt@</code>

List of priorities for students.

- first field is the student identifier
- second field is the identifier of the project topic
- third field is the priority number (or rank)
- fourth field is the power weight used in the paper (this is not
  needed but included to facilitate reproducibility)  


#+BEGIN_EXAMPLE 
f721a356abf2d2a635fb5de74740e8ff;59;1
f721a356abf2d2a635fb5de74740e8ff;49;2
f721a356abf2d2a635fb5de74740e8ff;50;3
f721a356abf2d2a635fb5de74740e8ff;56;4
f721a356abf2d2a635fb5de74740e8ff;63;5
f721a356abf2d2a635fb5de74740e8ff;67;6
f721a356abf2d2a635fb5de74740e8ff;1;7
fbd97a97bd6426ca20b778f615b15378;21;1
fbd97a97bd6426ca20b778f615b15378;32;2
fbd97a97bd6426ca20b778f615b15378;33;3
fbd97a97bd6426ca20b778f615b15378;76;4
#+END_EXAMPLE





- Files in receive students.txt and projects.txt

- run trunk/scripts/convert.sh to make these files in utf8
  NOT needed if the file is already in UTF8!!!! 

- run scripts/prepare_data.py data/2017

- ../scripts/prepare-data.py -d . 
  # # check anonymize=FALSE if for admin =TRUE if
  # # to publish data 

- create tmp_types.txt as for the year.
  states to which projects studnets can be assigned.
  "famarci"; "alle","farmaci"
  "not farmaci"; "alle", "alle ikke farmaci"


- run scripts/resume.R data/2017 to check the names of the
  types. they are changed in prepare_data.py

- launch2014.sh 
  # # edit script (with owa)
  # # edit load_data with starting high minimax
  # # first run to find out minmax
  # # consider three solutions 
  # # minimax_instab_greedy_max
  # # minimax_instab_weighted + owa
  # # minimax_instab_weighted + identity
  # # solution chosen between 1 and 3
  writes in res and sln

- src/report_sol.py -d data/2015 -s sln/sol_001.txt
  # edit for Studieretininger
  writes in out

- analysis.R to produce popularity table

- gnumeric out/output3.txt 

- gnumeric out/output4.csv -> save as popularity.xls

- Publish solution at:
  http://www.imada.sdu.dk/~marco/Teaching/FF501/Ekstern/2016/out/
  username: nat501
  password: FF33








* Data for Psychology



Rscript remove_duplicates.R



* Process for Psychology

Rscript scripts/analysis.R
./prepare-data.py -d .
vi tmp_types.txt


685  python3 src/main.py -d data/2018-psy -m minimax
686  python3 src/main.py -d data/2018-psy -m minimax_instab_greedy_max
687  python3 src/main.py -d data/2018-psy -m minimax_instab_weighted -W owa
688  python3 src/main.py -d data/2018-psy -m minimax_instab_weighted -W powers
  
make psy

google-chrome out/popularity.html
cp sln/sol_001.txt out
src/report_sol.py -d data/2018-psy -s sln/sol_001.txt

cp res/2018-psy-owa-minimax_instab_weighted.txt out
cp -r out ~/WWWpublic/Psychology/2018/


