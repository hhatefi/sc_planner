class EntityType:
    PROD=0
    COMP=1
    TRAN=2

class ProductPriority:
    LOW=0
    HIGH=1

class Entity:
    """ An entity in supply chain"""

    def __init__(self, entity_type):
        self._entity_type=entity_type

    def get_type(self):
        return self._entity_type

class Product(Entity):
    """The product class"""

    def __init__(self, name, order_size, priority=ProductPriority.LOW):
        """constructs a product"""
        super(Product, self).__init__(EntityType.PROD)
        self._name=name
        self._order_size=order_size
        self._priority=priority

class Component(Entity):
    """The component class"""

    def __init__(self, name, stock):
        """constructs a component"""
        super(Component, self).__init__(EntityType.COMP)
        self._name=name
        self._stock=stock

class TransitionType:
    """The type of transition"""
    AND=0
    OR=1
    DIR=2 # the target can be supplied directly by a supplier

class Transition(Entity):
    """The transition class"""

    def __init__(self, sources, target, tr_type):
        """constructs a transition"""
        super(Transition, self).__init__(EntityType.TRAN)
        self._sources=sources
        self._target=target
        self._tr_type=tr_type
        if self._tr_type == TransitionType.DIR:
            self._sources=None
