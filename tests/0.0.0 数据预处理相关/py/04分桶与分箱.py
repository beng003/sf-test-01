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

vdf = create_df(data, {alice: 0.3, bob: 0.7}, axis=0)

print('KBinsDiscretizer:\n', sf.reveal(KBinsDiscretizer(vdf['target']).partitions[bob].data))

sf.shutdown()
