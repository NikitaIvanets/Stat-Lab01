"""Запуск: python -m unittest -v test_lab.py. В дополнение к 27 тестам ноутбука."""
import unittest
from types import SimpleNamespace
import numpy as np
from generators import EmpiricalInverse, EmpiricalAlias

class GeneratorContract(unittest.TestCase):
    def test_alias_mass_and_boundaries(self):
        for observations in [[1],[0,1,1,1],[0,0,1,2,3,3,3,3]]:
            inv=EmpiricalInverse(observations);ali=EmpiricalAlias(observations)
            np.testing.assert_allclose(ali.reconstructed_mass(),inv.p,atol=1e-14)
            np.testing.assert_equal(inv.ppf(inv.cdf[:-1]),inv.values[1:])
    def test_repeatability_and_domain(self):
        for cls in [EmpiricalInverse,EmpiricalAlias]:
            g=cls([2.9,3.1,3.1,3.4])
            a=g.rvs(1000,np.random.default_rng(19));b=g.rvs(1000,np.random.default_rng(19))
            np.testing.assert_equal(a,b)
            self.assertTrue(np.isin(a,g.values).all())
            self.assertEqual(g.rvs(0,np.random.default_rng()).shape,(0,))
    def test_invalid_inputs(self):
        for cls in [EmpiricalInverse,EmpiricalAlias]:
            for x in [[],[np.nan],[np.inf],[[1,2]]]:
                with self.assertRaises(ValueError):cls(x)
            for size in [-1,True,1.5]:
                with self.assertRaises(ValueError):cls([1,2]).rvs(size,np.random.default_rng())
    def test_shared_context_and_marimo_sections(self):
        from interactive_context import load_context
        from lab_interactive import payload
        from app_marimo import app
        context=load_context()
        self.assertEqual(len(context['train'].query('wine_type == "white"')),3917)
        self.assertEqual(len(context['train'].query('wine_type == "red"')),1279)
        _,defs=app.run()
        self.assertEqual(defs['section'].value,'eda')
        for kind in ['eda','models','generator','diamond_pair']:
            spec=payload(kind,context)
            self.assertGreater(max(len(spec.get('data',[])),len(spec.get('train',[]))),1000)

if __name__=='__main__':unittest.main()
