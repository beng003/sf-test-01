import pandas as pd
from scr.preprocessing import *
import secretflow as sf
from secretflow.utils.simulation.data.dataframe import create_df
from secretflow.security.aggregation import SecureAggregator
# from secretflow.security import SecureAggregator
from secretflow.security.compare import SPUComparator
from sklearn.metrics import roc_auc_score

import secretflow as sf
from secretflow.data import FedNdarray, PartitionWay
from secretflow.device.driver import reveal
from secretflow.ml.boost.ss_xgb_v import Xgb

# Check the version of your SecretFlow
print('The version of SecretFlow: {}'.format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(['alice', 'bob'], address='local')
alice = sf.PYU('alice')
bob = sf.PYU('bob')
# 生成一个示例数据集

aggr = SecureAggregator(device=alice, participants=[alice, bob])

spu_device = sf.SPU(sf.utils.testing.cluster_def(parties=["alice", "bob"]))
comp = SPUComparator(spu_device)

from sklearn.datasets import load_breast_cancer

ds = load_breast_cancer()
x, y = ds['data'], ds['target']

v_data = FedNdarray(
    {
        alice: (alice(lambda: x[:, :15])()),
        bob: (bob(lambda: x[:, 15:])()),
    },
    partition_way=PartitionWay.VERTICAL,
)
label_data = FedNdarray(
    {alice: (alice(lambda: y)())},
    partition_way=PartitionWay.VERTICAL,
)

import pandas as pd

df = pd.DataFrame(ds['data'], columns=ds["feature_names"])
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
xgb = Xgb(spu_device)
model = xgb.train(params, v_data, label_data)
print('模型：', model)

yhat = model.predict(v_data)
yhat = reveal(yhat)
print(f"auc: {roc_auc_score(y, yhat)}")

a = sf.reveal(model.get_weights())
print('模型权重：', a)
