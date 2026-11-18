from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from IPython.display import display

def load_context():
    root=Path(__file__).resolve().parent
    SEED=504843
    def rng_for(offset=0):return np.random.Generator(np.random.PCG64(SEED+offset))
    COLS=['pH','residual sugar','alcohol']
    red=pd.read_csv(root/'data/winequality-red.csv',sep=';')
    white=pd.read_csv(root/'data/winequality-white.csv',sep=';')
    df=pd.concat([red.assign(wine_type='red'),white.assign(wine_type='white')],ignore_index=True)
    diamonds=pd.read_csv(root/'data/diamonds.csv')
    N=len(df)
    
    TRAIN_SHARE = 0.80
    
    group_id = df.groupby(list(df.columns), sort=False).ngroup()
    is_train = np.zeros(len(df), dtype=bool)
    
    r_split = rng_for(1)
    for wt in ['red', 'white']:
        mask = df['wine_type'].eq(wt)
        gid = group_id[mask]
        sizes = gid.value_counts(sort=False).sort_index()
        ids = sizes.index.to_numpy().copy()
        r_split.shuffle(ids)
        cum_rows = np.cumsum(sizes.loc[ids].to_numpy())
        train_ids = ids[cum_rows <= TRAIN_SHARE * mask.sum()]
        is_train[mask.to_numpy()] = gid.isin(train_ids).to_numpy()
    
    is_train = pd.Series(is_train, index=df.index, dtype=bool)
    train = df[is_train].copy()
    holdout = df[~is_train].copy()
    
    overlap = pd.merge(train.drop_duplicates(), holdout.drop_duplicates(), how='inner')
    assert len(overlap) == 0, 'Одинаковые строки попали в обе части'
    assert len(train) + len(holdout) == N
    
    table = pd.crosstab(
        df['wine_type'],
        pd.Series(
            np.where(is_train, 'Для настройки', 'Для проверки'),
            index=df.index
        )
    )
    
    table = table.rename(index={
        'red': 'Красное',
        'white': 'Белое'
    })
    
    table.index.name = 'Тип вина'
    table.columns.name = None
    
    # @title Код расчёта { display-mode: "form" }
    wine_labels = {
        'red': 'Красное вино',
        'white': 'Белое вино'
    }
    
    distribution_labels = {
        'normal': 'Нормальное',
        'lognormal': 'Логнормальное',
        'gamma': 'Гамма'
    }
    
    fits = {}
    fit_rows = []
    
    for color in ['red', 'white']:
        for col in COLS:
    
            x = train.loc[train['wine_type'] == color, col].to_numpy()
            y = holdout.loc[holdout['wine_type'] == color, col].to_numpy()
    
            if col == 'pH':
                candidates = {
                    'normal': stats.norm
                }
            else:
                candidates = {
                    'normal': stats.norm,
                    'lognormal': stats.lognorm,
                    'gamma': stats.gamma
                }
    
            for name, dist in candidates.items():
    
                if name == 'normal':
                    pars = dist.fit(x)
                else:
                    pars = dist.fit(x, floc=0)
    
                model = dist(*pars)
                fits[(color, col, name)] = model
    
                k = 2
    
                fit_rows.append({
                    'тип': color,
                    'величина': col,
                    'модель': name,
                    'параметры SciPy': str(
                        tuple(float(round(v, 6)) for v in pars)
                    ),
                    'BIC_train': (
                        k * np.log(len(x))
                        - 2 * model.logpdf(x).sum()
                    ),
                    'NLL_holdout': -model.logpdf(y).mean(),
                    'KS_D_holdout': stats.kstest(
                        y, model.cdf
                    ).statistic
                })
    fit_table = pd.DataFrame(fit_rows)
    
    return locals()
