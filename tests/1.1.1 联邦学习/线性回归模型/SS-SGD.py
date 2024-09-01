# note:SSRegression() 使用秘密分享协议实现了针对垂直划分数据集的线性回归和二分类回归训练，求解方式为批量随机梯度下降。
# 线性回归 拟合系数为 w = (w1, …, wp) 的线性模型，目标为最小化数据集中标签值与线性近似的预测值之间的残差平方和。
# 逻辑回归 是以分类为目标的线性模型。逻辑回归在文献中也称为 logic 回归、最大熵分类 (MaxEnt) 或对数线性分类器。通过逻辑函数将线性预测结果转换为样本的概率结果。该方法同时提供可选的L2 正则化选项来防止过拟合。

import sys
import time
import logging

import numpy as np
import spu
import secretflow as sf
from secretflow.data.split import train_test_split
from secretflow.device.driver import wait, reveal
from secretflow.data import FedNdarray, PartitionWay
from secretflow.ml.linear.ss_sgd import SSRegression

from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

# init log
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# init all nodes in local Standalone Mode.
sf.init(['alice', 'bob', 'carol'], address='local')

# init PYU, the Python Processing Unit, process plaintext in each node.
alice = sf.PYU('alice')
bob = sf.PYU('bob')
carol = sf.PYU('carol')

# init SPU, the Secure Processing Unit,
#           process ciphertext under the protection of a multi-party secure computing protocol
spu = sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob', 'carol']))

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

# alice / bob / carol each hold one third of the features of the data
# read_x is execute locally on each node.
v_data = FedNdarray(
    partitions={
        alice: alice(read_x)(0, 10),
        bob: bob(read_x)(10, 20),
        carol: carol(read_x)(20, 30),
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
v_train_data, v_test_data = train_test_split(v_data, train_size=split_factor, random_state=random_state)
v_train_label, v_test_label = train_test_split(label_data, train_size=split_factor, random_state=random_state)
# run SS-SGD
# SSRegression use spu to fit model.
model = SSRegression(spu)
start = time.time()
model.fit(
    v_train_data,      # x
    v_train_label,  # y
    5,           # epochs
    0.3,         # learning_rate
    32,          # batch_size
    't1',        # sig_type
    'logistic',  # reg_type
    'l2',        # penalty
    0.1,         # l2_norm
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