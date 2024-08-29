import secretflow as sf
from scr.utils import *
from secretflow.data.horizontal import read_csv as h_read_csv
from secretflow.security.aggregation import SecureAggregator
# from secretflow.security import SecureAggregator
from secretflow.security.compare import SPUComparator

sf.init(['alice', 'bob'], address='local')
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# The aggregator and comparator are respectively used to aggregate
# or compare data in subsequent data analysis operations.
aggr = SecureAggregator(device=alice, participants=[alice, bob])

spu = sf.SPU(sf.utils.testing.cluster_def(parties=["alice", "bob"]))
comp = SPUComparator(spu)

# 初始化数据路径
path_manager = PathManager()
ALICE_PATH = path_manager.get_path("ALICE_PATH")
BOB_PATH = path_manager.get_path("BOB_PATH")
h_alice_path = ALICE_PATH / "h_alice.csv"
h_bob_path = BOB_PATH / "h_bob.csv"
v_alice_path = str(ALICE_PATH / "v_alice.csv")
v_bob_path = str(BOB_PATH / "v_bob.csv")

hdf = h_read_csv(
    {
        alice: h_alice_path,
        bob: h_bob_path
    },
    aggregator=aggr,
    comparator=comp,
)

hdf.drop(columns=["uid"], inplace=True)

print(table_statistics_vh(hdf))

from secretflow.data.vertical import read_csv as v_read_csv

# xxx: 纵向联邦学习数据读取接口数据路径仅限字符串类型
vdf = v_read_csv(
    {
        alice: v_alice_path,
        bob: v_bob_path
    },
    spu=spu,
    keys="uid",
    drop_keys="uid",
    psi_protocl="ECDH_PSI_2PC",
)
print(table_statistics_vh(vdf))

# note:数据属性和方法参考连接
# https://www.secretflow.org.cn/zh-CN/docs/secretflow/v1.8.0b0/source/secretflow.data.core.data.core.pandas
# https://www.secretflow.org.cn/zh-CN/docs/secretflow/v1.8.0b0/source/secretflow.data.data.horizontal#secretflow.data.horizontal.HDataFrame
# https://www.secretflow.org.cn/zh-CN/docs/secretflow/v1.8.0b0/source/secretflow.data.data.vertical#secretflow.data.vertical.VDataFrame

# 以下是部分测试
print('列标签：', vdf.columns)
print('数据类型：', vdf.dtypes)
print('形状：', vdf.shape)
print('值：', vdf.values)
print('计数：', vdf.count())
print('总和：', vdf.sum())
print('最小值：', vdf.min())
print('最大值：', vdf.max())
print('平均值：', vdf.mean())
print('是否为空：', vdf.isna())

# xxx: HDataFrame raise NotImplementedError(),功能暂未实现
# todo: 可参考标准化数据实现以下部分功能
## quantile(self, q=0.5, axis=0)
## kurtosis(self, *args, **kwargs):
## skew(self, *args, **kwargs):
## sem(self, *args, **kwargs):
## std(self, *args, **kwargs): # todo:参考/mnt/users/beng003/anaconda3/envs/sf/lib/python3.10/site-packages/secretflow/preprocessing/scaler.py的StandardScaler
## var(self, *args, **kwargs):
## replace(self, *args, **kwargs):
## mode(self, *args, **kwargs):
## index(self) -> list:
## value_counts(self, *args, **kwargs) -> pd.Series:
## iloc(self, index: Union[int, slice, List[int]]) -> 'HDataFrame':
## rename(self, *args, **kwargs) -> Union['HDataFrame', None]:
## pow(self, *args, **kwargs) -> 'HDataFrame':
## round(self, *args, **kwargs) -> 'HDataFrame':
## select_dtypes(self, *args, **kwargs) -> 'HDataFrame':
## subtract(self, *args, **kwargs) -> 'HDataFrame':

# xxx: VDataFrame raise NotImplementedError(),功能暂未实现
## index(self) -> list:
## iloc(self, index: Union[int, slice, List[int]]) -> 'VDataFrame':
## rename(self, *args, **kwargs) -> Union['VDataFrame', None]:

sf.shutdown()
