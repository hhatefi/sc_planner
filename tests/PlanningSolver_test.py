import os
import unittest

from context import parser as pr
from context import supply_chain as sc
from context import solver as sl

class PlanningSolverTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PlanningSolverTest, self).__init__(*args,**kwargs)
        self._examples_dir=os.path.join(os.path.dirname(__file__), '..', 'examples')
        self._test_model_dir=os.path.join(os.path.dirname(__file__), 'test_models')

    def _get_solver(self, path_to_model):
        par=pr.Parser(path_to_model)
        stmts=par.parse()
        spch=sc.SupplyChain(stmts)
        return sl.PlanningSolver(spch)

    def _get_solver_example(self, model_fname):
        return self._get_solver(os.path.join(self._examples_dir,model_fname))

    def _get_solver_testmodel(self, model_fname):
        return self._get_solver(os.path.join(self._test_model_dir,model_fname))

    def test_compute_upper_bounds(self):
        slvr=self._get_solver_testmodel('upper_bound.txt')
        uppper_bound_dict=slvr._compute_upper_bounds()
        self.assertEqual(uppper_bound_dict['p1'],3)
        self.assertEqual(uppper_bound_dict['p2'],8)
        self.assertEqual(uppper_bound_dict['c1'],3)
        self.assertEqual(uppper_bound_dict['c2'],11)
        self.assertEqual(uppper_bound_dict['c3'],11)
        self.assertEqual(uppper_bound_dict['c4'],8)
        self.assertEqual(uppper_bound_dict['c5'],14)


if __name__=='__main__':
    unittest.main()
