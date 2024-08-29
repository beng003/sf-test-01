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

hdf = h_read_csv(
    {alice: h_alice_path, bob: h_bob_path},
    aggregator=aggr,
    comparator=comp,
)

hdf.drop(columns=["uid"], inplace=True)

print(table_statistics_vh(hdf))


from secretflow.data.vertical import read_csv as v_read_csv

# xxx: 纵向联邦学习数据读取接口数据路径仅限字符串类型
vdf = v_read_csv(
    {alice: v_alice_path, bob: v_bob_path},
    spu=spu,
    keys="uid",
    drop_keys="uid",
    psi_protocl="ECDH_PSI_2PC",
)
print(table_statistics_vh(vdf))

sf.shutdown()
