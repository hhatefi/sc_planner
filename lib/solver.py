import pulp

import lib.entities as en

class Solver:
    """The solver class solves a problem on supply chain
    """
    def __init__(self, supply_chain):
        self._supply_chain=supply_chain
        self._initialize()

    def _initialize(self):
        """initializes the problem before solving"""
        pass

    def _solve(self):
        """solves the problem"""
        pass

class PlanningSolver(Solver):
    """The solver class for supply chain planning"""

    def __init__(self, supply_chain):
        super(PlanningSolver, self).__init__(supply_chain)

    def _initialize(self):
        self._prob=pulp.LpProblem("Supply chain planning", pulp.LpMaximize) # creating the problem

        spch=self._supply_chain # the supply chain
        prods=spch._products    # the products in the supply chain
        comps=spch._components  # the components in the supply chain
        trans=spch._transitions # the transitions in the supply chain

        ### variable definition ###
        # a variable for each product
        prod_vars=dict([(p._name,pulp.LpVariable(p._name,0,p._order_size)) for p in prods])
        # a variable for each inventory with positive stock
        inv_vars=dict([("_i_"+c._name,pulp.LpVariable("_i_"+c._name,0,c._stock)) for c in comps if c._stock > 0])
        # a variable for each supplier with is connected to an entity
        sup_vars=dict([("_s_"+t._target,pulp.LpVariable("_s_"+t._target,0)) for t in trans if t._tr_type == en.TransitionType.DIR])
        # a variable for each transition between two entities
        trans_var_pairs=[]
        for t in trans:
            if t._sources:
                trans_var_pairs.extend([(f"_{s}_{t._target}",pulp.LpVariable(f"_{s}_{t._target}",0)) for s in t._sources])
        trans_vars=dict(trans_var_pairs)
        # a variable for each branch of or operators
        or_var_list=dict([(t._target, [pulp.LpVariable(f"_x_{s}_{t._target}",0,1,pulp.LpInteger) for s in t._sources]) for t in trans if t._tr_type == en.TransitionType.OR])

        ### constraints ###
        # or variable constraints: sum of or variables must be 1
        for _,or_vars in or_var_list.items():
            self._prob += pulp.lpSum(or_vars) == 1
        # computing the upper bound of inflow into entities
        upper_bounds=self._compute_upper_bounds()
        # conservation law constraints
        for t in trans:
            target=t._target
            # computing outflow
            if self.is_product(target): # if the transition target is a product, the outflow goes all into the product
                outflow=prod_vars[target]
            else: # otherwise the transition target is a component, so we need to find the outflow
                outgoing_trans=spch._outgoings[target] #the outgoing transitions
                outflow=pulp.lpSum([trans_vars[f"_{target}_{ot._target}"] for ot in outgoing_trans])

            ### computing inflow and adding conservation law contraint
            # add the inventory to the inflow if its stock is positive
            inflow=inv_vars[f"_i_{target}"] if self.has_positive_stock(target) else 0
            if t._tr_type == en.TransitionType.AND: # if transition is an AND transition
                if t._sources:
                    for s in t._sources:
                        self._prob+=outflow==trans_vars[f"_{s}_{target}"]+inflow
            elif t._tr_type == en.TransitionType.OR: # if transition is an OR transition
                if t._sources:
                    for n,s in enumerate(t._sources):
                        self._prob+=outflow-inflow <= trans_vars[f"_{s}_{target}"]+(1-or_var_list[target][n])*upper_bounds[target]
                        self._prob+=outflow-inflow >= trans_vars[f"_{s}_{target}"]-(1-or_var_list[target][n])*upper_bounds[target]
            else: # the transition is a direct transition from supplier to an entity
                inflow+=sup_vars[f"_s_{target}"]
                self._prob+=outflow==inflow
        # add leaf contrains
        for leaf in spch._leaves:
            # computing outflow
            if self.is_product(leaf): # if the transition target is a product, the outflow goes all into the product
                outflow=prod_vars[leaf]
            else: # otherwise the transition target is a component, so we need to find the outflow
                outgoing_trans=spch._outgoings[leaf] #the outgoing transitions
                outflow=pulp.lpSum([trans_vars[f"_{leaf}_{ot._target}"] for ot in outgoing_trans])
            # add the inventory to the inflow if its stock is positive
            inflow=inv_vars[f"_i_{leaf}"] if self.has_positive_stock(leaf) else 0
            self._prob+=outflow==inflow

        # the objective: Maximize the sum of products and the sum of inventory outflows
        self._prob += pulp.lpSum([v for _,v in prod_vars.items()]) + pulp.lpSum([inv for _,inv in inv_vars.items()])

    def _compute_upper_bounds(self):
        """computes upper bound on inflow into any entity.
           It is essential for linearization of OR constraints.
           It returns a dictionary mapping an entity name into its upper bound flow.
        """
        spch=self._supply_chain # the supply chain
        prods=spch._products    # the products in the supply chain
        trans=spch._transitions # the transitions in the supply chain

        upper_bound_dict=dict([(p._name,p._order_size) for p in prods])

        # keep updating the upper bound until reaching a fixed point
        done=False
        while not done:
            done=True
            for t in trans:
                if t._target not in upper_bound_dict:
                    ub=0
                    updated=True
                    for out_tr in spch._outgoings[t._target]:
                        if out_tr._target in upper_bound_dict:
                            ub += upper_bound_dict[out_tr._target]
                        else:
                            updated=False
                            break
                    if updated:
                        upper_bound_dict[t._target]=ub
                        done=False
                    else:
                        continue
        return upper_bound_dict

    def solve(self):
        self._prob.solve()

    def write_lp(self, filename):
        self._prob.writeLP(filename)

    def is_product(self, name):
        return self._supply_chain._entity_dict[name].get_type() == en.EntityType.PROD

    def has_positive_stock(self, name):
        ent=self._supply_chain._entity_dict[name]
        return ent.get_type() == en.EntityType.COMP and ent._stock > 0

    def objective(self):
        """returns the optimal value"""
        return pulp.value(self._prob.objective)

    def __str__(self):
        prob=self._prob
        status=f"Status: {pulp.LpStatus[prob.status]}"
        obj=f"Objective={self.objective()}"
        opt_vals='\n'.join([f"{v.name}={v.varValue}" for v in prob.variables()])
        return f"{status}\n\n{obj}\n\n{opt_vals}"
