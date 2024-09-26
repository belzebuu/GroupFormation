# GroupFormation

Method for grouping students presented in:

> Z. Sun, M. Chiarandini (2021). An exact algorithm for group formation
> to promote collaborative learning. In M. Warschauer, G. Lynch (Eds.),
> LAK21: 11th International Learning Analytics and Knowledge Conference
> (LAK21), April 12--16, 2021, Irvine, CA, USA, Association for
> Computing Machinery, New York, NY, USA. [[Paper](doc/lak21-57.pdf)],
> [[Presentation](doc/lak21-57_ppp.pdf)]


> M. Chiarandini, Z. Sun (2024). Team Formation with Diversity and Similarity Goals. Proceedings of PATAT 2024, Copenhagen. [[Paper](doc/patat2024_4532.pdf)].



## Data

Input data are to be collected in an Excel file containing the sheets
and format described below. An example of input data is available `data/example/data.xlsx`.

#### students

List of students. The first 9 columns must have the same column name as
in the example file. Columns that are not relevant can be left white. 
Most of the times `grp_id` is the same
as `student_id`; However, it is possible via `group` and `grp_id` to preassign some students in the same team. The
columns after the 10th must specify the characteristics that we want to
use for forming the teams. The names of these columns are arbitrary but
must be the same as used in the sheet `dtypes`.

#### dtypes

Three columns indicating for a `Variable`, ie, characteristics, the
`Type` (`category` for categorical and `float64` or `int64` for numerical) and the
`Priority`. `Priority=` 1 means that the characteristics is the first and most important in priority.
`Heterogeneous` is whether hetergeneity within the groups should be promoted (1) or avoided (-1). A value of (0) currently ignores the categorical characteristics while for numerical characteristics it maximizes the minimum and the sum of the divergencies thus implementing another form of heterogeneity. 


#### teams

Placeholders for the teams.  Here we specify how many teams and how many students are allowed in each team. The labels of the columns must be kept as in the example. Teams can be organized for convenience in groups and subgroups. This organization has no impact on the formation. The `type` is used to create
different collections of teams. For example, in a course with students from different study programs (curricula) one might want to form teams with only students from the same study program. 


#### types

The compatibilities between team and student types, for example to handle different study programs. Each line
contains a type that is the `team_type` and a type `student_type` that is compatible
with it.
If a type is compatible with several types, the pairwise compatibilities go rowwise.


#### restrictions

Currently not implemented, leave empty.




## Run the Program

To run the program you need the commercial solver [Gurobi](https://www.gurobi.com/) with the Python interface. If that is available you can test this program with: 

```
make 
```

Change the DATA parameter in the Makefile for solving your own data set.

## Contact

For more information contact the maintainer: `marco@imada.sdu.dk`.
