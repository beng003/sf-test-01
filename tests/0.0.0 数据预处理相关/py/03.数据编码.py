from scr.preprocessing import *
import secretflow as sf
from secretflow.utils.simulation.data.dataframe import create_df

# Check the version of your SecretFlow
print('The version of SecretFlow: {}'.format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(['alice', 'bob'], address='local')
alice = sf.PYU('alice')
bob = sf.PYU('bob')

import pandas as pd
from sklearn.datasets import load_iris

iris = load_iris(as_frame=True)
data = pd.concat([iris.data, iris.target], axis=1)

# In order to facilitate the subsequent display,
# here we first set some data to None.
data.iloc[1, 1] = None
data.iloc[100, 1] = None

# Restore target to its original name.
data['target'] = data['target'].map({
    0: 'setosa',
    1: 'versicolor',
    2: 'virginica'
})

vdf = create_df(data, {alice: 0.3, bob: 0.7}, axis=1)

print('OneHotEncoder:', OneHotEncoder(vdf['target']))
print('LabelEncoder:', LabelEncoder(vdf['target']))
print('OrdinalEncoder:', OrdinalEncoder(vdf['target']))

from secretflow.utils.simulation.datasets import load_linear

vdf = load_linear(parts={alice: (1, 4), bob: (18, 22)})

spu_devices = sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob']))
print(
    'WOEEncoder:',
    WOEEncoder(
        spu_devices,
        vdf,
        binning_method="quantile",
        bin_num=5,
        bin_names={
            alice: ["x1", "x2", "x3"],
            bob: ["x18", "x19", "x20"]
        },
        label_name="y",
    ))

sf.shutdown()
