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
import spu

from secretflow.ml.boost.sgb_v import (
    Sgb,
    get_classic_XGB_params,
    get_classic_lightGBM_params,
)

# Check the version of your SecretFlow
print('The version of SecretFlow: {}'.format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(['alice', 'bob'], address='local')
alice = sf.PYU('alice')
bob = sf.PYU('bob')
# 生成一个示例数据集

# HEU settings
heu_config = {
    'sk_keeper': {
        'party': 'alice'
    },
    'evaluators': [{
        'party': 'bob'
    }],
    'mode': 'PHEU',
    'he_parameters': {
        # ou is a fast encryption schema that is as secure as paillier.
        'schema': 'ou',
        'key_pair': {
            'generate': {
                # bit size should be 2048 to provide sufficient security.
                'bit_size': 2048,
            },
        },
    },
    'encoding': {
        'cleartext_type': 'DT_I32',
        'encoder': "IntegerEncoder",
        'encoder_args': {
            "scale": 1
        },
    },
}

alice = sf.PYU('alice')
bob = sf.PYU('bob')
heu = sf.HEU(heu_config, spu.spu_pb2.FM128)
print("Alice and Bob are ready to go!")

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
params = get_classic_XGB_params()
params['num_boost_round'] = 3
params['max_depth'] = 3

sgb = Sgb(heu)
model = sgb.train(params, v_data, label_data)

yhat = model.predict(v_data)
yhat = reveal(yhat)
print(f"auc: {roc_auc_score(y, yhat)}")

sf.shutdown()

