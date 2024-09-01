#note:HESS-SGD模块 HESSLogisticRegression() 混合使用同态加密和Secret Sharing实现了可证安全的线性回归.
# 和SS-SGD最大的区别在于：将SS-SGD中通讯开销最大的梯度计算替换为纯本地的同态计算实现。由于同态加密的非对称特性，目前HESS-SGD只支持2方计算。算法实现参考 <When Homomorphic Encryption Marries Secret Sharing: Secure Large-Scale Sparse Logistic Regression and Applications in Risk Control>，并进行一些工程优化改造。


import sys
import time
import logging

import numpy as np
import secretflow as sf
from secretflow.data.split import train_test_split
from secretflow.device.driver import wait, reveal
from secretflow.data import FedNdarray, PartitionWay
from secretflow.ml.linear.hess_sgd import HESSLogisticRegression

from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

# init log
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# init all nodes in local Standalone Mode. HESS-SGD only support 2PC
sf.init(['alice', 'bob'], address='local')

# init PYU, the Python Processing Unit, process plaintext in each node.
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# init SPU, the Secure Processing Unit,
# process ciphertext under the protection of a multi-party secure computing protocol
spu = sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob']))

# first, init a HEU device that alice is sk_keeper and bob is evaluator
heu_config = sf.utils.testing.heu_config(sk_keeper='alice', evaluators=['bob'])
heu_x = sf.HEU(heu_config, spu.cluster_def['runtime_config']['field'])

# then, init a HEU device that bob is sk_keeper and alice is evaluator
heu_config = sf.utils.testing.heu_config(sk_keeper='bob', evaluators=['alice'])
heu_y = sf.HEU(heu_config, spu.cluster_def['runtime_config']['field'])


# read data in each party
def read_x(start, end):
    # use breast_cancer as example
    from sklearn.datasets import load_breast_cancer
    from sklearn.preprocessing import StandardScaler
    x = load_breast_cancer()['data']
    # LR's train dataset must be standardized or normalized
    scaler = StandardScaler()
    x = scaler.fit_transform(x)
    return x[:, start:end]


def read_y():
    from sklearn.datasets import load_breast_cancer
    return load_breast_cancer()['target']


# alice / bob  each hold half of the features of the data
# read_x is execute locally on each node.
v_data = FedNdarray(
    partitions={
        alice: alice(read_x)(0, 15),
        bob: bob(read_x)(15, 30),
    },
    partition_way=PartitionWay.VERTICAL,
)
# Y label belongs to alice
label_data = FedNdarray(
    partitions={alice: alice(read_y)()},
    partition_way=PartitionWay.VERTICAL,
)

# wait IO finished
wait([p.data for p in v_data.partitions.values()])
wait([p.data for p in label_data.partitions.values()])
# split train data and test data
random_state = 1234
split_factor = 0.8
v_train_data, v_test_data = train_test_split(v_data,
                                             train_size=split_factor,
                                             random_state=random_state)
v_train_label, v_test_label = train_test_split(label_data,
                                               train_size=split_factor,
                                               random_state=random_state)
# run HESS-SGD
# HESSLogisticRegression use spu / heu to fit model.
model = HESSLogisticRegression(spu, heu_y, heu_x)
# spu – SPU SPU device.
# heu_y – HEU device without label.
# heu_x – HEU device with label.
# Here, label belong to Alice(heu_x)
start = time.time()
model.fit(
    v_train_data,
    v_train_label,
    learning_rate=0.3,
    epochs=5,
    batch_size=32,
)
logging.info(f"train time: {time.time() - start}")

# Do predict
start = time.time()
# Now the result is saved in the spu by ciphertext
spu_yhat = model.predict(v_test_data)
# reveal for auc, acc and classification report test.
yhat = reveal(spu_yhat)
logging.info(f"predict time: {time.time() - start}")
y = reveal(v_test_label.partitions[alice])
# get the area under curve(auc) score of classification
logging.info(f"auc: {roc_auc_score(y, yhat)}")
binary_class_results = np.where(yhat > 0.5, 1, 0)
# get the accuracy score of classification
logging.info(f"acc: {accuracy_score(y, binary_class_results)}")
# get the report of classification
print("classification report:")
print(classification_report(y, binary_class_results))
