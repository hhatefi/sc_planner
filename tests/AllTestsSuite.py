import unittest

import Statement_test
import Parser_test
import SupplyChain_test
import PlanningSolver_test


loader=unittest.TestLoader()
suite=unittest.TestSuite()

suite.addTest(loader.loadTestsFromModule(Statement_test))
suite.addTest(loader.loadTestsFromModule(Parser_test))
suite.addTest(loader.loadTestsFromModule(SupplyChain_test))
suite.addTest(loader.loadTestsFromModule(PlanningSolver_test))

runner=unittest.TextTestRunner(verbosity=3)
result=runner.run(suite)
