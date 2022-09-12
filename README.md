# GroupFormation

Method for grouping students presented in:

> Z. Sun, M. Chiarandini (2021). An exact algorithm for group formation
> to promote collaborative learning. In M. Warschauer, G. Lynch (Eds.),
> LAK21: 11th International Learning Analytics and Knowledge Conference
> (LAK21), April 12--16, 2021, Irvine, CA, USA, Association for
> Computing Machinery, New York, NY, USA. [[Paper](doc/lak21-57.pdf)],
> [[Presentation](doc/lak21-57_ppp.pdf)]



## Data

Input data are to be collected in an Excel file containing the sheets
and format described below. An example that you can use as starting
point can be found in `data/example/data.xlsx`.

#### students

List of students. The first 9 columns must have the same column name as
in the example file. Not all columns are relevant: `grp_id` is the same
as `student_id`; `group` and `priority_list` can be left white. The
columns from the 10th on are the characteristics that we want to
consider in the grouping. The names of these columns are arbitrary but
must be the same as used in the sheet `dtypes`.

#### dtypes

Three columns indicating for a `Variable`, ie, characteristics, the
`Type` (`category` for categorical and `float64` for numerical) and the
`Priority`. `Priority=` 1 is the highest priority.

#### projects

Here we specify how many groups and how many students in each group we
want to have. The labels of the columns must be kept as in the
example. `team` can be left empty. The `type` is used to create
different collections of groups. For example, one might want to have
students belonging to a study program be all grouped in groups with
students from the same study program. 

#### types

Here we express the compatibilities between study programs. Each line
contains a type that is the `key` and a type `type` that is compatible
with it.


#### restrictions

Currently not implemented, leave empty.


## Run the Program

To run the program you need the commercial solver [Gurobi](https://www.gurobi.com/) with the Python interface. If that is available you can test this program with: 

```
make 
```

Change the DATA parameter in the Makefile for solving your own data set.

## Contact

For more information contact the maintainer: marco@imada.sdu.dk.
