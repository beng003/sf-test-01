# fixme:无法执行

import secretflow as sf

# Check the version of your SecretFlow
print('The version of SecretFlow: {}'.format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(['alice', 'bob', 'charlie'], address='local')
alice, bob = sf.PYU('alice'), sf.PYU('bob')

from secretflow.data.horizontal import read_csv
from secretflow.security.aggregation import SecureAggregator
from secretflow.security.compare import SPUComparator
from secretflow.utils.simulation.datasets import load_dermatology

aggr = SecureAggregator(alice, [alice, bob])
spu = sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob']))
comp = SPUComparator(spu)
data = load_dermatology(parts=[alice, bob], aggregator=aggr, comparator=comp)
data = data[0:5]
data.fillna(value=0, inplace=True)

params = {
    "num_boost_round": 10,  # Number of boosting iterations, default is 10
    "max_depth": 5,  # Maximum depth of a tree, default is 5
    "learning_rate": 0.3,  # Step size shrinkage, default is 0.3
    "objective": "logistic",  # Learning objective, default is 'logistic'
    "reg_lambda": 0.1,  # L2 regularization term, default is 0.1
    "subsample": 1,  # Subsample ratio of the training instances, default is 1
    "colsample_by_tree": 1,  # Subsample ratio of columns, default is 1
    "sketch_eps": 0.1,  # Number of bins for sketching, default is 0.1
    "base_score": 0,  # Initial prediction score, default is 0
    "seed": 42,  # Pseudorandom number generator seed, default is 42
}

from secretflow.ml.boost.homo_boost import SFXgboost

bst = SFXgboost(server=alice, clients=[alice, bob])
bst.train(data, data, params=params, num_boost_round=6)

print(bst)
print('计算完成')
sf.shutdown()
