import os
import unittest

from context import parser as pr
from context import supply_chain as sc
from context import entities as en

class SupplyChainTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SupplyChainTest, self).__init__(*args, **kwargs)
        self._examples_dir=os.path.join(os.path.dirname(__file__), '..', 'examples')
        self._test_model_dir=os.path.join(os.path.dirname(__file__), 'test_models')

    def _run_an_example(self, model_fname):
        p=pr.Parser(os.path.join(self._examples_dir, model_fname))
        statements=p.parse()
        return sc.SupplyChain(statements)

    def _run_a_test_model(self, model_fname):
        p=pr.Parser(os.path.join(self._test_model_dir, model_fname))
        statements=p.parse()
        return sc.SupplyChain(statements)

    def test_extraction1(self):
        spch=self._run_an_example('example1.txt')
        self.assertTrue(spch._products)
        self.assertTrue(spch._components)
        self.assertTrue(spch._transitions)
        # len
        self.assertEqual(len(spch._products),2)
        self.assertEqual(len(spch._components),2)
        self.assertEqual(len(spch._transitions),3)
        # products
        self.assertEqual(spch._products[0]._name,'p1')
        self.assertEqual(spch._products[1]._name,'p2')
        self.assertEqual(spch._products[0]._order_size,10)
        self.assertEqual(spch._products[1]._order_size,10)
        self.assertEqual(spch._products[0]._priority,en.ProductPriority.HIGH)
        self.assertEqual(spch._products[1]._priority,en.ProductPriority.LOW)
        # components
        self.assertEqual(spch._components[0]._name,'c1')
        self.assertEqual(spch._components[1]._name,'c2')
        self.assertEqual(spch._components[0]._stock,0)
        self.assertEqual(spch._components[1]._stock,10)
        # transitions
        self.assertEqual(spch._transitions[0]._target,'c1')
        self.assertEqual(spch._transitions[1]._target,'p1')
        self.assertEqual(spch._transitions[2]._target,'p2')
        self.assertTrue(spch._transitions[0]._sources is None)
        self.assertTrue(spch._transitions[1]._sources)
        self.assertTrue(spch._transitions[2]._sources)
        self.assertEqual(len(spch._transitions[1]._sources),2)
        self.assertEqual(len(spch._transitions[2]._sources),1)
        self.assertEqual(spch._transitions[1]._sources[0],'c1')
        self.assertEqual(spch._transitions[1]._sources[1],'c2')
        self.assertEqual(spch._transitions[2]._sources[0],'c2')
        self.assertEqual(spch._transitions[0]._tr_type,en.TransitionType.DIR)
        self.assertEqual(spch._transitions[1]._tr_type,en.TransitionType.OR)
        self.assertEqual(spch._transitions[2]._tr_type,en.TransitionType.AND)

    def test_extraction2(self):
        spch=self._run_an_example('example2.txt')
        self.assertTrue(spch._products)
        self.assertTrue(spch._components)
        self.assertTrue(spch._transitions)
        # len
        self.assertEqual(len(spch._products),1)
        self.assertEqual(len(spch._components),4)
        self.assertEqual(len(spch._transitions),4)
        # products
        self.assertEqual(spch._products[0]._name,'p')
        self.assertEqual(spch._products[0]._order_size,20)
        self.assertEqual(spch._products[0]._priority,en.ProductPriority.LOW)
        # components
        self.assertEqual(spch._components[0]._name,'c1')
        self.assertEqual(spch._components[1]._name,'c2')
        self.assertEqual(spch._components[2]._name,'c3')
        self.assertEqual(spch._components[3]._name,'c4')
        self.assertEqual(spch._components[0]._stock,0)
        self.assertEqual(spch._components[1]._stock,0)
        self.assertEqual(spch._components[2]._stock,0)
        self.assertEqual(spch._components[3]._stock,20)
        # transitions
        self.assertEqual(spch._transitions[0]._target,'p')
        self.assertEqual(spch._transitions[1]._target,'c1')
        self.assertEqual(spch._transitions[2]._target,'c2')
        self.assertEqual(spch._transitions[3]._target,'c3')
        self.assertTrue(spch._transitions[0]._sources)
        self.assertTrue(spch._transitions[1]._sources)
        self.assertTrue(spch._transitions[2]._sources)
        self.assertTrue(spch._transitions[3]._sources is None)
        self.assertEqual(len(spch._transitions[0]._sources),2)
        self.assertEqual(len(spch._transitions[1]._sources),2)
        self.assertEqual(len(spch._transitions[2]._sources),1)
        self.assertEqual(spch._transitions[0]._sources[0],'c1')
        self.assertEqual(spch._transitions[0]._sources[1],'c2')
        self.assertEqual(spch._transitions[1]._sources[0],'c3')
        self.assertEqual(spch._transitions[1]._sources[1],'c4')
        self.assertEqual(spch._transitions[2]._sources[0],'c4')
        self.assertEqual(spch._transitions[0]._tr_type,en.TransitionType.AND)
        self.assertEqual(spch._transitions[1]._tr_type,en.TransitionType.AND)
        self.assertEqual(spch._transitions[2]._tr_type,en.TransitionType.AND)
        self.assertEqual(spch._transitions[3]._tr_type,en.TransitionType.DIR)

    def test_verify_the_chain(self):
        # product duplicate
        with self.assertRaises(ValueError):
            self._run_a_test_model('dup_prod.txt')
        # component duplicate
        with self.assertRaises(ValueError):
            self._run_a_test_model('dup_comp.txt')
        # component/product duplicate
        with self.assertRaises(ValueError):
            self._run_a_test_model('dup_prod_comp.txt')
        # transition duplicate (from comp/product to comp/product)
        with self.assertRaises(ValueError):
            self._run_a_test_model('dup_tran1.txt')
        # transition duplicate (from comp/product to supplier)
        with self.assertRaises(ValueError):
            self._run_a_test_model('dup_tran2.txt')
        # non existing target
        with self.assertRaises(KeyError):
            self._run_a_test_model('non_existing_target.txt')
        # non existing source
        with self.assertRaises(KeyError):
            self._run_a_test_model('non_existing_source.txt')
        # self loop
        with self.assertRaises(ValueError):
            self._run_a_test_model('self_loop.txt')

    def test_build_outgoings(self):
        spch=self._run_a_test_model('build_outgoings.txt')
        for p in spch._products:
            self.assertTrue(p not in spch._outgoings) # Products have no outgoing transition
        self.assertEqual(len(spch._outgoings['c1']),3)
        self.assertTrue(spch._outgoings['c1'][0] is spch._transitions[0])
        self.assertTrue(spch._outgoings['c1'][1] is spch._transitions[1])
        self.assertTrue(spch._outgoings['c1'][2] is spch._transitions[2])
        self.assertEqual(len(spch._outgoings['c2']),2)
        self.assertTrue(spch._outgoings['c2'][0] is spch._transitions[0])
        self.assertTrue(spch._outgoings['c2'][1] is spch._transitions[3])
        self.assertEqual(len(spch._outgoings['c3']),2)
        self.assertTrue(spch._outgoings['c3'][0] is spch._transitions[0])
        self.assertTrue(spch._outgoings['c3'][1] is spch._transitions[2])
        self.assertEqual(len(spch._outgoings['c4']),2)
        self.assertTrue(spch._outgoings['c4'][0] is spch._transitions[2])
        self.assertTrue(spch._outgoings['c4'][1] is spch._transitions[3])
        self.assertTrue('c2' in spch._leaves)
        self.assertTrue('c3' in spch._leaves)

if __name__ == '__main__':
    unittest.main()
