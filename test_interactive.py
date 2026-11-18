"""Cross-check browser statistics against SciPy, not against their own code."""
import json
import subprocess
import unittest
from pathlib import Path
import numpy as np
from scipy import stats, special

ROOT = Path(__file__).resolve().parent
STUB = r'''
const {mountLab}=require('./interactive_engine.js');
function el(tag='div'){return {tagName:tag.toUpperCase(),value:'',textContent:'',innerHTML:'',append(){},setAttribute(){},addEventListener(){}}}
global.document={createElement:el};global.Plotly={react(){},purge(){}};
const root={innerHTML:'',querySelector(){return el()}};
const panel=mountLab(root,{kind:'mass',data:[{carat:1,price:100,cut:'Ideal'},{carat:1,price:200,cut:'Ideal'}]});
const f=panel.functions;
'''

def js(expression):
    return json.loads(subprocess.check_output(['node','-e',STUB+'\nconsole.log(JSON.stringify('+expression+'));'],cwd=ROOT,text=True))

class BrowserStatisticsTests(unittest.TestCase):
    def test_distribution_functions(self):
        cases = [(-2,3),(0,3),(1.5,7),(5,100)]
        actual = js('['+','.join(f'f.tCDF({x},{df})' for x,df in cases)+']')
        np.testing.assert_allclose(actual,[stats.t.cdf(x,df) for x,df in cases],atol=2e-11)
        cases2 = [(1,2),(.5,5),(10,30),(5,.1)]
        actual=js('['+','.join(f'f.gammaQ({a},{x})' for a,x in cases2)+']')
        np.testing.assert_allclose(actual,[special.gammaincc(a,x) for a,x in cases2],atol=2e-11)
        probs=[.001,.025,.5,.975,.999]
        np.testing.assert_allclose(js(f'{json.dumps(probs)}.map(f.normalQ)'),stats.norm.ppf(probs),atol=1e-10)

    def test_correlations_and_distances(self):
        x=[1,1,2,4,8,9,12,12];y=[5,2,3,8,7,7,10,12]
        got=js(f'(()=>{{let x={x},y={y};return [f.corr(x,y),f.corr(f.ranks(x),f.ranks(y)),f.ks(x,y)]}})()')
        np.testing.assert_allclose(got,[stats.pearsonr(x,y).statistic,stats.spearmanr(x,y).statistic,stats.ks_2samp(x,y).statistic],atol=1e-12)

    def test_sampling_and_generators(self):
        got=js('(()=>{let a=[1,2,3,4,5],x=f.sample(a,5,f.random(42),false),y=f.empirical([1,1,2,4],40000,f.random(43),"alias"),z=f.gammaDraw(40000,.7,2,f.random(44));return [new Set(x).size,f.mean(y),f.variance(y,0),f.mean(z),f.variance(z,0),JSON.stringify(f.sample(a,20,f.random(42),true))===JSON.stringify(f.sample(a,20,f.random(42),true))]})()')
        self.assertEqual(got[0],5)
        np.testing.assert_allclose(got[1:3],[2,1.5],atol=.04)
        np.testing.assert_allclose(got[3:5],[1.4,2.8],rtol=.05)
        self.assertTrue(got[5])

    def test_wine_contingency_against_scipy(self):
        import pandas as pd
        data=pd.read_csv(ROOT/'data/winequality-white.csv',sep=';')
        x=data.pH.tolist();y=data.alcohol.tolist()
        got=js(f'f.association({json.dumps(x)},{json.dumps(y)},4)')
        tab=pd.crosstab(pd.qcut(data.pH,4,duplicates='drop'),pd.qcut(data.alcohol,4,duplicates='drop'))
        chi,p,df,expected=stats.chi2_contingency(tab,correction=False)
        np.testing.assert_allclose([got['χ²'],got['df'],got['Cramér V'],got['min ожидаемая']],[chi,df,np.sqrt(chi/(len(data)*min(np.array(tab.shape)-1))),expected.min()],rtol=1e-11)

if __name__=='__main__':unittest.main()
