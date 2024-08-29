from scr.preprocessing import *
import secretflow as sf
from secretflow.utils.simulation.data.dataframe import create_df
from secretflow.security.aggregation import SecureAggregator
# from secretflow.security import SecureAggregator
from secretflow.security.compare import SPUComparator
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

aggr = SecureAggregator(device=alice, participants=[alice, bob])

spu = sf.SPU(sf.utils.testing.cluster_def(parties=["alice", "bob"]))
comp = SPUComparator(spu)

hdf = create_df(data, {
    alice: 0.3,
    bob: 0.7
},
                axis=0,
                aggregator=aggr,
                comparator = comp)

print('MinMaxScaler:\n',
      sf.reveal(MinMaxScaler(hdf['sepal length (cm)']).partitions[alice].data))
print(
    'StandardScaler:\n',
    sf.reveal(
        StandardScaler(
            df=hdf['sepal length (cm)'],
            with_mean=True,
            with_std=True,
            aggregator=aggr,
        ).partitions[alice].data))

sf.shutdown()
