# todo: 参考secretflow.utils.simulation.data.dataframe.create_df
# xxx: 抽样数据的返回形式

from scr.preprocessing import *

import secretflow as sf
from scr.utils import *

# Check the version of your SecretFlow
print("The version of SecretFlow: {}".format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(["alice", "bob"], address="local")
alice, bob = sf.PYU("alice"), sf.PYU("bob")

from secretflow.data.horizontal import read_csv as h_read_csv
from secretflow.security.aggregation import SecureAggregator
# from secretflow.security import SecureAggregator
from secretflow.security.compare import SPUComparator

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

# sample_algorithm_obj = SampleAlgorithmFactory().create_sample_algorithm(
#     input_df=vdf,
#     total_num=vdf.shape[0]-2,  # 假设数据集有1000行
#     sample_algorithm="random",  # 随机抽样
#     random_frac=0.8,  # 抽样比例为80%
#     random_random_state=42,  # 固定随机种子，保证可重复性
#     random_replacement=False,  # 不允许重复抽样
#     # system_frac=None,  # 非系统抽样，传 None
#     # stratify_frac=None,  # 非分层抽样，传 None
#     stratify_random_state=None,
#     stratify_observe_feature=None,
#     stratify_replacements=None,
#     quantiles=None,
#     weights=None,
# )

# 执行抽样
sample_df, report_results = vdf_sample(
    input_df=vdf,
    total_num=vdf.shape[0],  # 假设数据集有1000行
    sample_algorithm="random",  # 随机抽样
    random_frac=0.8,  # 抽样比例为80%
    random_random_state=42,  # 固定随机种子，保证可重复性
    random_replacement=False,  # 不允许重复抽样
    # system_frac=None,  # 非系统抽样，传 None
    # stratify_frac=None,  # 非分层抽样，传 None
    stratify_random_state=None,
    stratify_observe_feature=None,
    stratify_replacements=None,
    quantiles=None,
    weights=None,
)

print(sf.reveal(sample_df.partitions[alice].data))
print(report_results)
sf.shutdown()
