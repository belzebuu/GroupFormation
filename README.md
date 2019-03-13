Project Assignment
==================

This repository contains the software to assign students to
projects. The project is described in:

M. Chiarandini, R. Fagerberg, S. Gualandi (2017). [Handling
preferences in student-project
allocation](https://doi.org/10.1007/s10479-017-2710-1). Annals of
Operations Research.

We assume given a set of project topics each with a subset of teams
available with bounded size, and a set of students with preferences on
the project topics. The task is to create teams of students to work on
the available project topics.

A further side constraint that is not discussed in the article is
included: projects and students belong to a type, for example study
programs and there are compatibility constraints.


We assume that there is a local installation of
[Gurobi](http://www.gurobi.com) and that its module for python is in
the python path of the system.

In the following we describe how to define the input data and the work
flow.

-   Original Data
-   Transformed Data
-   Workflow

Original Data
-------------

We need four textual comma separeted files `projects.csv`,
`students.csv`, `types.csv` and `restrictions.csv`.

`projects.csv` contains data on the project topics, the number of
teams for each topic and the capacity of each group. Other information
is probably not relevant.

The file has no header. Each field is separeted by semicolumn `;`.
There is one line for each different team of a topic. Each line contains
the following fields:

-   Topic identifier (eg, a number equal for all teams in the topic)
-   Team identifier
-   Title or topic
-   Min capacity
-   Max capacity
-   Projet type, eg, study program
-   Project identifier (a combination of topic and team identifier)
-   Offering institute abbreviation
-   Offering institute full name
-   Need complementary short courses
-   Working location

Example:

```{.example}
1;a;Algorithms to identify something from something else;3;5;alle studier, dog ikke farmaci;01a;IMADA;Institut for Matematik og Datalogi;Skriftlig formidling og rapportskrivning (online),Rapportskrivning med LaTeX,Posterfremstilling;IMADA
1;b;Algorithms to identify something from something else;3;5;alle studier, dog ikke farmaci;01b;IMADA;Institut for Matematik og Datalogi;Skriftlig formidling og rapportskrivning (online),Rapportskrivning med LaTeX,Posterfremstilling;IMADA
2;;Alternative topic in project topics;3;5;alle studier, dog ikke farmaci;02;BI;Biologisk Institut;Skriftlig formidling og rapportskrivning (online),Naturvidenskabelig informationskompetence,Posterfremstilling;Biologisk Institut
3;...
```

`students.csv` contains details on the students.

The file has no header. Each field is separeted by semicolumn `;`.
There is a line for each student enrolled. Each line contains the
following fields:

-   Group identifier (different students may have the same group
    identifier if they enrolled together meaning that they want ot end
    in the same tems).
-   Username
-   Student type, eg, study program 
-   Priority list (comma separated list of topic identifiers sorted in decreasing order of preference)
-   Student identifier
-   Studen full name
-   Email address
-   Registration timestamp (we assume a setting in which only the registration with the latest timestamp is reported)


```{.example}
1;sffd90;biomedicin;9,75,76,65,44,39,41;XXXXXXXXXX;Mario Rossi;mario.rossi@student.org;2018-03-03 09:14:11
2;sffe90;biomedicin;82,68,22,46,65,90,75,30,8,76,51;YYYYYYYYYY;Sabrina Rossi;sabrina.rossi@student.org;2018-03-03 10:54:50
3;...
```



`types.csv` contains information about the compatibility between
student and project types: for each student type, it provides the list
of acceptable project types. The line starts with the student type and
continues with an arbitrary number of acceptable project types.  It is
not necessary that the project types are the same as the student
types, although in the example of study programs, they indeed are
supposed to be the same. Types are separeted by semicolon.


`restrictions.csv` specifications of the restrictions on the number of
teams open across different topics. For example, if the project topics
26 and 40 are offered each to a maximum of two teams but the teacher
responsible for both only wants to open at most two projects overall.

Example:
```
2;26;40
2;78;95
2;27;86
```


Transformed Data
================

TODO: remove need for data transformation 

The assignment program needs currently five files:

- `tmp_projects.txt`
- `tmp_students.txt`
- `tmp_priorities.txt`
- `types.csv`
- `restrictions.csv`

An example is provided in `data/2016`

Fields are separated by semicolon.  The file `types.csv` is the
same as described above. The first three files are obtained by parsing
the original data with the script ```scripts/prepare-data.py```.


`tmp_projects.txt`
------------------

List of projects. In each line:

-   first field is an identifier of the topic
-   second field an identifier for the team. The field is empty if only
    one team allowed
-   fourth and fifth fields are the lower and upper bound of team size,
    respectively
-   the sixth field is the area of the project.

``` {.example}
1;;3;5;nat501
2;;3;5;alle
3;;3;5;nat507
4;;4;5;alle
5;;3;5;alle
6;;3;5;alle
7;a;3;3;nat501
7;b;3;3;nat501
```

`tmp_students.txt`
-----------------

List of students and groups. In each line:

-   first field is the group identifier
-   second field is the student id
-   third field is the type of the student

``` {.example}
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
```

`tmp_priorities.txt`
-------------------

List of priorities for students.

-   first field is the student identifier
-   second field is the identifier of the project topic
-   third field is the priority number (or rank)
-   fourth field is the power weight used in the paper (this is not
    needed but included to facilitate reproducibility)

``` {.example}
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
```

`types.csv`
-----------

As explained above

``` {.example}
"biologi";"alle";"natbidat"
"farmaci";"alle";"farmaci"
"natbidat";"alle";"natbidat"
```

`restrictions.csv`
------------------


```
2;26;40
2;78;95
2;27;86
```





Work flow
=========


- In a directory, for example, `data/2016` prepare the input in
   `projects.csv`, `students.csv` and `types.csv`

- Make sure the encoding of the files is UTF8. If that is not the case
    you can run `scripts/convert.sh [dirname]` to make these files in utf8.

- Prepare the data in the transformed format: run

  ```
  scripts/prepare-data.py -d data/2016
  ```

  Add the flag `-p` to make feasible the assignment of students to
  projects that are not in their preference list. This might be needed
  if no solution can otherwise be found.

- We find the worst priority that must be used in order to find a
  feasible assignment. This is the minimax approach of the paper:

  ```
  python3 src/main.py -d data/2016 -m minimax | tee 2016-minimax.txt
  ```
  
  The value found for the worst priority has to be put in the dictionary in `src/load_data.py`.
  TODO: change this.



- We solve the problem by

  ```
  python3 src/main.py -d data/2016 -m minimax_instab_weighted -W owa | tee 2018-minimax_instab_weighted-owa.txt
  ```
  This is the OWA approach of the paper.

  Alternatively, you can use one of the other two approaches: 

  ```
  python3 src/main.py -d data/2016 -m minimax_instab_weighted -W powers | tee 2018-minimax_instab_weighted-powers.txt
  python3 src/main.py -d data/2016 -m minimax_instab_weighted -W identity | tee 2018-minimax_instab_weighted-identity.txt
  ```
  These approaches produce assignments of different quality to choose from.

  The solutions are written in the directory `sln`


- Rewrite the solution with more details and different formats. 

  ```
  python3 src/report_sol.py -d data/2016 -s sln/sol_001.txt
  ```

  It reads the original data files and outputs in `out`.


Interpretation of results:

- `out/outputs4.csv` is a popularity table. Use `scripts/analysis.R`
   to produce popularity table in an html page from `out/outputs4.csv`

- import `out/output3.txt` in a spreadsheet
