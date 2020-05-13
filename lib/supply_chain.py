import lib.parser as pr


class SupplyChain:
    """Supply chain class represents a supply chain
    """

    def __init__(self, statements):
        """constructs a supply chain from the statements parsed from a supply chain
           description.
        """
        self._extract_entities(statements)
        self._verify_the_chain()
        self._build_outgoings()

    def _extract_entities(self, statements):
        """extracts different entities (products, components and transitions) from
           @param statements
        """
        self._products=[]
        self._components=[]
        self._transitions=[]

        for stmt in statements:
            stmt_type=stmt.get_type()
            if stmt_type==pr.StatementType.PROD_DEF:
                self._products.extend(stmt._products)
            elif stmt_type==pr.StatementType.COMP_DEF:
                self._components.extend(stmt._components)
            else:
                self._transitions.append(stmt._transition)

    def _verify_the_chain(self):
        """verifies in the chain that
           - products and components are only once defined
           - there is no undefined product or component in any transition
           - there in no self loop on any product or transition
        """
        # checking product duplicates
        self._entity_dict={}
        seen=self._entity_dict
        for p in self._products:
            if p._name not in seen:
                seen[p._name]=p
            else:
                raise ValueError(f'"{p._name}" was defined multiple times.')
        # checking component duplicates
        for c in self._components:
            if c._name not in seen:
                seen[c._name]=c
            else:
                raise ValueError(f'"{c._name}" was defined multiple times.')
        # checking transition duplicates
        tseen=set()
        for t in self._transitions:
            if t._target not in seen:
                raise KeyError(f'"{t._target}" has not been defined.')
            if t._sources:
                if t._target in t._sources: # a self loop
                    raise ValueError(f'A self loop exist on "{t._target}"')
                for s in t._sources:
                    if s not in seen:
                        raise KeyError(f'"{s}" has not been defined.')
                    if (s, t._target) not in tseen:
                        tseen.add((s,t._target))
                    else:
                        raise ValueError(f'Transition from "{s}" to "{t._target}" was defined multiple times.')
            else:
                if (None, t._target) not in tseen:
                    tseen.add((None,t._target))
                else:
                    raise ValueError(f'Transition from supplier to "{t._target}" was defined multiple times.')

    def _build_outgoings(self):
        """builds the dictionary of each entity name mapped into the list of its outgoing transitions.
           The dictionary is used when formulating planning LP.
           It creates dictionary self._outgoings.
        """
        self._outgoings={}
        self._leaves=set(self._entity_dict.keys())
        for tr in self._transitions:
            self._leaves.discard(tr._target)
            if tr._sources:
                for src in tr._sources:
                    if src in self._outgoings:
                        self._outgoings[src].append(tr)
                    else:
                        self._outgoings[src]=[tr]

        
