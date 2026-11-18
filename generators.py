import numpy as np

class EmpiricalInverse:
    def __init__(self, observations):
        x=np.asarray(observations,dtype=float)
        if x.ndim!=1 or x.size==0 or not np.isfinite(x).all():
            raise ValueError('Нужен непустой одномерный массив конечных чисел')
        self.values,counts=np.unique(x,return_counts=True)
        self.p=counts/counts.sum();self.cdf=np.cumsum(self.p);self.cdf[-1]=1.0
    def ppf(self,u):
        u=np.asarray(u,dtype=float)
        if not np.isfinite(u).all() or np.any((u<0)|(u>=1)):
            raise ValueError('u должно принадлежать [0,1)')
        return self.values[np.searchsorted(self.cdf,u,side='right')]
    def rvs(self,size,rng):
        if isinstance(size,bool) or not isinstance(size,(int,np.integer)) or size<0:
            raise ValueError('size должно быть целым неотрицательным')
        return self.ppf(rng.random(size))



class EmpiricalAlias(EmpiricalInverse):
    def __init__(self,observations):
        super().__init__(observations)
        k=len(self.p);scaled=self.p*k
        self.prob=np.ones(k);self.alias=np.arange(k)
        small=list(np.flatnonzero(scaled<1));large=list(np.flatnonzero(scaled>=1))
        while small and large:
            s=small.pop();l=large.pop();self.prob[s]=scaled[s];self.alias[s]=l
            scaled[l]-=1-scaled[s]
            (small if scaled[l]<1 else large).append(l)
    def rvs(self,size,rng):
        if isinstance(size,bool) or not isinstance(size,(int,np.integer)) or size<0:
            raise ValueError('size должно быть целым неотрицательным')
        j=rng.integers(0,len(self.p),size=size);u=rng.random(size)
        return self.values[np.where(u<self.prob[j],j,self.alias[j])]
    def reconstructed_mass(self):
        k=len(self.p);mass=self.prob/k
        np.add.at(mass,self.alias,(1-self.prob)/k)
        return mass

