Supply Chain Planner
====================

This project solves planning problem on a supply chain graph. The
chain should be defined in a text file with specific format. This
document briefly describe how to install and use the planner.


## Prerequisite

To run the planner, pythen 3.6 and above is required. It also
formulates the planning problem as an MILP (mixed integer linear
program). Hence, it requires to use an MILP solver. It uses
[PuLP](https://pypi.org/project/PuLP/) as the linear programming
modeller, which can call several external
solvers. [CBC](http://www.coin-or.org/) solver, which is bundled with
PuLP should be enough for test purposes.  PuLP can be installed via
`pip`, i.e.

```SHELL
# pip install pulp
```

or using `make` (at project root directory):

```SHELL
$ make init
```

## Usage
The usage of the planner is as follows:

```SHELL
$ python planner.py <model> [<lp>]
```

- <model> is the chain described by the input format (see examples).

- <lp> is the name of output file containing the mixed linear integer
  program corresponding to the model. This argument is optional.
