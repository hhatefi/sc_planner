import unittest

from context import parser as pr
from context import entities as en

class StatementTest(unittest.TestCase):

    def test_factory(self):
        # a single product
        p=pr.Statement.factory("product p1=10 high")
        self.assertEqual(p.get_type(), pr.StatementType.PROD_DEF)

        # a single component
        p=pr.Statement.factory("component c1=7")
        self.assertEqual(p.get_type(), pr.StatementType.COMP_DEF)

        # an AND transition
        p=pr.Statement.factory("p1<-c1+c2")
        self.assertEqual(p.get_type(), pr.StatementType.TRAN_DEF)

        # an invalid statement
        with self.assertRaises(ValueError):
            pr.Statement.factory(":p1<-c1+c2")

        # another invalid statement
        with self.assertRaises(ValueError):
            pr.Statement.factory(".")

    def test_product_parsing(self):
        # an empty product definition
        with self.assertRaises(ValueError):
           pr.Statement.factory("product")
        # another empty product definition
        with self.assertRaises(ValueError):
           pr.Statement.factory("product\n\t")

        # a single product
        p=pr.Statement.factory("product p1=10 high")
        self.assertEqual(p.get_type(), en.EntityType.PROD)
        self.assertEqual(len(p._products), 1)
        self.assertEqual(p._products[0]._name, 'p1')
        self.assertEqual(p._products[0]._order_size, 10)
        self.assertEqual(p._products[0]._priority, en.ProductPriority.HIGH)

        # two products
        p=pr.Statement.factory("product\n _pp1=5 high,_pp2=3")
        self.assertEqual(p.get_type(), en.EntityType.PROD)
        self.assertEqual(len(p._products), 2)
        self.assertEqual(p._products[0]._name, '_pp1')
        self.assertEqual(p._products[0]._order_size, 5)
        self.assertEqual(p._products[0]._priority, en.ProductPriority.HIGH)
        self.assertEqual(p._products[1]._name, '_pp2')
        self.assertEqual(p._products[1]._order_size, 3)
        self.assertEqual(p._products[1]._priority, en.ProductPriority.LOW)

    def test_component_parsing(self):
        # an empty component definition
        with self.assertRaises(ValueError):
           pr.Statement.factory("component")
        # another empty component definition
        with self.assertRaises(ValueError):
           pr.Statement.factory("component\n\t")

        # a single component
        p=pr.Statement.factory("component c1=7")
        self.assertEqual(p.get_type(), en.EntityType.COMP)
        self.assertEqual(len(p._components), 1)
        self.assertEqual(p._components[0]._name, 'c1')
        self.assertEqual(p._components[0]._stock, 7)

        # two products
        p=pr.Statement.factory("component\n _cc1=9   \t,_ccc,dd")
        self.assertEqual(p.get_type(), en.EntityType.COMP)
        self.assertEqual(len(p._components), 3)
        self.assertEqual(p._components[0]._name, '_cc1')
        self.assertEqual(p._components[0]._stock, 9)
        self.assertEqual(p._components[1]._name, '_ccc')
        self.assertEqual(p._components[1]._stock, 0)
        self.assertEqual(p._components[2]._name, 'dd')
        self.assertEqual(p._components[2]._stock, 0)

    def test_transition_parsing(self):
        # an invalid transition
        with self.assertRaises(ValueError):
            pr.Statement.factory('1p1<-')
        # another invalid transition
        with self.assertRaises(ValueError):
            pr.Statement.factory('pp4p_1 <<')
        # an OR transition
        p=pr.Statement.factory("p1 <- a | c2")
        self.assertEqual(p._transition._target, 'p1')
        self.assertEqual(len(p._transition._sources), 2)
        self.assertEqual(p._transition._sources[0],'a')
        self.assertEqual(p._transition._sources[1],'c2')
        self.assertEqual(p._transition._tr_type, en.TransitionType.OR)

        # an AND transition
        p=pr.Statement.factory("ppp1<-_cc1+_c2")
        self.assertEqual(p._transition._target, 'ppp1')
        self.assertEqual(len(p._transition._sources), 2)
        self.assertEqual(p._transition._sources[0],'_cc1')
        self.assertEqual(p._transition._sources[1],'_c2')
        self.assertEqual(p._transition._tr_type, en.TransitionType.AND)

        # direct connection to supplier
        p=pr.Statement.factory("cc1 <- supplier")
        self.assertEqual(p._transition._target, 'cc1')
        self.assertEqual(p._transition._sources, None)
        self.assertEqual(p._transition._tr_type, en.TransitionType.DIR)

        # another AND transition
        p=pr.Statement.factory("""__p1<-r+_c2+
                                    dd1+dd4
                                    +cc2""")
        self.assertEqual(p._transition._target, '__p1')
        self.assertEqual(len(p._transition._sources), 5)
        self.assertEqual(p._transition._sources[0],'r')
        self.assertEqual(p._transition._sources[1],'_c2')
        self.assertEqual(p._transition._sources[2],'dd1')
        self.assertEqual(p._transition._sources[3],'dd4')
        self.assertEqual(p._transition._sources[4],'cc2')
        self.assertEqual(p._transition._tr_type, en.TransitionType.AND)

if __name__=='__main__':
    unittest.main()
