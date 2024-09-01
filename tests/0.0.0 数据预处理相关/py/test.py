import pandas as pd
from scr.preprocessing import *
import secretflow as sf
from secretflow.utils.simulation.data.dataframe import create_df
from secretflow.security.aggregation import SecureAggregator
# from secretflow.security import SecureAggregator
from secretflow.security.compare import SPUComparator
import pandas as pd


# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(['alice', 'bob'], address='local')
alice = sf.PYU('alice')
bob = sf.PYU('bob')
# 生成一个示例数据集

aggr = SecureAggregator(device=alice, participants=[alice, bob])

spu = sf.SPU(sf.utils.testing.cluster_def(parties=["alice", "bob"]))
comp = SPUComparator(spu)

data = {
    'feature_1': [1, 2, 3, None, 5],
    'feature_2': [None, 1, None, 4, 5],
    'feature_3': [1, None, 3, 4, None]
}
data = pd.DataFrame(data)
df = create_df(
    data,
    {
        alice: 0.3,
        bob: 0.7
    },
    axis=0,
    aggregator=aggr,
    comparator=comp,
)

print(random_sample(df))
print(sf.reveal(random_sample(df).partitions[alice].data))
print(sf.reveal(random_sample(df).partitions[bob].data))
sf.shutdown()

# print("原始数据集：\n", df)
# print("\n过滤后的数据集：\n", filtered_df)

# print(sf.reveal(filtered_df.partitions[alice].data))
# print(sf.reveal(filtered_df.partitions[bob].data))
