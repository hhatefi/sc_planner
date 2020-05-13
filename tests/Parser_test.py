import os
import unittest

from context import parser as pr
from context import entities as en


class ParserTest(unittest.TestCase):
    """Parser test"""

    def __init__(self, *args, **kwargs):
        super(ParserTest, self).__init__(*args, **kwargs)
        self._examples_dir=os.path.join(os.path.dirname(__file__), '..', 'examples')

    def _run_test(self, model_fname):
        p=pr.Parser(os.path.join(self._examples_dir, model_fname))
        return p.parse()

    def test_model1(self):
        stmts=self._run_test('example1.txt')
        self.assertTrue(stmts)
        self.assertEqual(len(stmts),5)
        # checking types
        self.assertEqual(stmts[0].get_type(), pr.StatementType.PROD_DEF)
        self.assertEqual(stmts[1].get_type(), pr.StatementType.COMP_DEF)
        self.assertEqual(stmts[2].get_type(), pr.StatementType.TRAN_DEF)
        self.assertEqual(stmts[3].get_type(), pr.StatementType.TRAN_DEF)
        self.assertEqual(stmts[4].get_type(), pr.StatementType.TRAN_DEF)
        ### checking the product defintion
        self.assertTrue(stmts[0]._products)
        self.assertEqual(len(stmts[0]._products), 2)
        self.assertEqual(stmts[0]._products[0]._name, 'p1')
        self.assertEqual(stmts[0]._products[0]._order_size, 10)
        self.assertEqual(stmts[0]._products[0]._priority, en.ProductPriority.HIGH)
        self.assertEqual(stmts[0]._products[1]._name, 'p2')
        self.assertEqual(stmts[0]._products[1]._order_size, 10)
        self.assertEqual(stmts[0]._products[1]._priority, en.ProductPriority.LOW)
        ### checking the component defintion
        self.assertTrue(stmts[1]._components)
        self.assertEqual(len(stmts[1]._components), 2)
        self.assertEqual(stmts[1]._components[0]._name, 'c1')
        self.assertEqual(stmts[1]._components[0]._stock, 0)
        self.assertEqual(stmts[1]._components[1]._name, 'c2')
        self.assertEqual(stmts[1]._components[1]._stock, 10)
        ### checking transitions
        self.assertTrue(stmts[2]._transition)
        self.assertTrue(stmts[3]._transition)
        self.assertTrue(stmts[4]._transition)
        # tr
        self.assertEqual(stmts[2]._transition._target, 'c1')
        self.assertTrue(stmts[2]._transition._sources is None)
        self.assertEqual(stmts[2]._transition._tr_type, en.TransitionType.DIR)
        # tr
        self.assertEqual(stmts[3]._transition._target, 'p1')
        self.assertTrue(stmts[3]._transition._sources)
        self.assertEqual(len(stmts[3]._transition._sources), 2)
        self.assertEqual(stmts[3]._transition._sources[0], 'c1')
        self.assertEqual(stmts[3]._transition._sources[1], 'c2')
        self.assertEqual(stmts[3]._transition._tr_type, en.TransitionType.OR)
        # tr
        self.assertEqual(stmts[4]._transition._target, 'p2')
        self.assertTrue(stmts[4]._transition._sources)
        self.assertEqual(len(stmts[4]._transition._sources), 1)
        self.assertEqual(stmts[4]._transition._sources[0], 'c2')
        self.assertEqual(stmts[4]._transition._tr_type, en.TransitionType.AND)

    def test_model2(self):
        stmts=self._run_test('example2.txt')
        self.assertTrue(stmts)
        self.assertEqual(len(stmts),7)
        # checking types
        self.assertEqual(stmts[0].get_type(), pr.StatementType.PROD_DEF)
        self.assertEqual(stmts[1].get_type(), pr.StatementType.COMP_DEF)
        self.assertEqual(stmts[2].get_type(), pr.StatementType.COMP_DEF)
        self.assertEqual(stmts[3].get_type(), pr.StatementType.TRAN_DEF)
        self.assertEqual(stmts[4].get_type(), pr.StatementType.TRAN_DEF)
        self.assertEqual(stmts[5].get_type(), pr.StatementType.TRAN_DEF)
        self.assertEqual(stmts[6].get_type(), pr.StatementType.TRAN_DEF)
        ### checking the product defintion
        self.assertTrue(stmts[0]._products)
        self.assertEqual(len(stmts[0]._products), 1)
        self.assertEqual(stmts[0]._products[0]._name, 'p')
        self.assertEqual(stmts[0]._products[0]._order_size, 20)
        self.assertEqual(stmts[0]._products[0]._priority, en.ProductPriority.LOW)
        ### checking the first component defintion
        self.assertTrue(stmts[1]._components)
        self.assertEqual(len(stmts[1]._components), 2)
        self.assertEqual(stmts[1]._components[0]._name, 'c1')
        self.assertEqual(stmts[1]._components[0]._stock, 0)
        self.assertEqual(stmts[1]._components[1]._name, 'c2')
        self.assertEqual(stmts[1]._components[1]._stock, 0)
        ### checking the second component defintion
        self.assertTrue(stmts[2]._components)
        self.assertEqual(len(stmts[2]._components), 2)
        self.assertEqual(stmts[2]._components[0]._name, 'c3')
        self.assertEqual(stmts[2]._components[0]._stock, 0)
        self.assertEqual(stmts[2]._components[1]._name, 'c4')
        self.assertEqual(stmts[2]._components[1]._stock, 20)
        ### checking transitions
        self.assertTrue(stmts[3]._transition)
        self.assertTrue(stmts[4]._transition)
        self.assertTrue(stmts[5]._transition)
        self.assertTrue(stmts[6]._transition)
        # tr
        self.assertEqual(stmts[3]._transition._target, 'p')
        self.assertTrue(stmts[3]._transition._sources)
        self.assertEqual(len(stmts[3]._transition._sources), 2)
        self.assertEqual(stmts[3]._transition._sources[0], 'c1')
        self.assertEqual(stmts[3]._transition._sources[1], 'c2')
        self.assertEqual(stmts[3]._transition._tr_type, en.TransitionType.AND)
        # tr
        self.assertEqual(stmts[4]._transition._target, 'c1')
        self.assertTrue(stmts[4]._transition._sources)
        self.assertEqual(len(stmts[4]._transition._sources), 2)
        self.assertEqual(stmts[4]._transition._sources[0], 'c3')
        self.assertEqual(stmts[4]._transition._sources[1], 'c4')
        self.assertEqual(stmts[4]._transition._tr_type, en.TransitionType.AND)
        # tr
        self.assertEqual(stmts[5]._transition._target, 'c2')
        self.assertTrue(stmts[5]._transition._sources)
        self.assertEqual(len(stmts[5]._transition._sources), 1)
        self.assertEqual(stmts[5]._transition._sources[0], 'c4')
        self.assertEqual(stmts[5]._transition._tr_type, en.TransitionType.AND)
        # tr
        self.assertEqual(stmts[6]._transition._target, 'c3')
        self.assertTrue(stmts[6]._transition._sources is None)
        self.assertEqual(stmts[6]._transition._tr_type, en.TransitionType.DIR)

if __name__ == '__main__':
    unittest.main()
