Supply Chain Planner
====================

This project solves planning problem on a supply chain graph. The
chain should be defined in a text file with specific format. This
document briefly describe how to install the planner, define a supply
chain and solve it.

## Method

The planner models a supply chain as a maximum flow problem, which is
then formulated as a mixed integer linear program and fed into the LP
solver. If you need a deeper look into the algorithm used for planning
see [this document](docs/planning.pdf).

## Prerequisite

To run the planner, pythen 3.6 and above is required. Since the
planner formulates the problem as an MILP (mixed integer linear
program), it also requires an MILP solver. It uses
[PuLP](https://pypi.org/project/PuLP/) as the linear programming
modeler, which can call several external
solvers. [CBC](http://www.coin-or.org/) solver, which is bundled with
PuLP should be enough for test purposes.  PuLP can be installed via
`pip`, i.e.

```SHELL
pip install pulp
```

or using `make` (at project root directory):

```SHELL
make init
```

## Usage
The usage of the planner is as follows:

```SHELL
python planner.py <model> [<lp>]
```

- `model` is the chain described by the input format (see [examples](examples)).

- `lp` is the name of output file containing the mixed linear integer
  program corresponding to the model. This argument is optional.

## Model specification

A supply chain specification comprises of *component* and
*product*. Products are at the final stage denoting the result of a
chain. An example of product declaration can be as follows.

```SHELL
product p1, p2=30;
```

As we want to maximize the production, the above line puts their sum
in the objective function. That is to say, the objective of this
supply chain will contain `p1+p2`. In addition, it imposes constraint
`p2<=30` on the plan to ensure the number of product `p2` is not above
30. Suppose the above line defines the whole chain, the induced MILP
looks like:

```SHELL
max p1 + p2
subject to
   p2 <= 30
   p1 and p2 are integer
```

It is indeed not a realistic chain, since a chain usually trace the
products back to suppliers and depots via components. Components
can be seen as the intermediate products between suppliers and
depots and the final products. They are defined in a similar way
as products. For instance,

```SHELL
component c1, c2=10;
```

defines component `c1` and `c2`, with `c2` being fed by an depot
of size 10. The semantics of this definition is constraint `c2<=10`,
which makes sure the number of component `c2` never goes above the
capacity of the depot. It is possible to connect the a component
directly to a supplier, e.g. by

```SHELL
c1<-supplier;
```

This means the supplier can deliver any number of `c1` required for
the plan. Components and products can be connected to each other to
produce other components and products. Operator `+` combines two or
more components and produces a result. As an example,

```SHELL
p1<-c1+c2
```

combines `n` items of component `c1` with `n` items of component `c2`
and yields `n` items of product `p1`. The semantics of this operator
is similar to **AND** gate, considering it obligates the same quantity
of `c1` and `c2` be available at the time. In the induced MILP, it
introduces the following constrains:

```SHELL
p1=c1
p1=c2
```

Components can likewise be combined by an **OR** gate.

```SHELL
p1<-c1|c2
```

In this case, `p1` is produced either of `c1` or `c2`, exclusively. It
introduces the following constrains:

```SHELL
x1 + x2 = 1
x1 * c1 + x2 * c2 = p1
x1 and x2 are binary
```

Binary variables `x1` and `x2` determine which component `c1` or
respectively `c2` is selected to produce `p1`. The constraints involve
multiplication of two variables and thereby not linear. Their
linearization is explain in detail [here](docs/planning.pdf).
