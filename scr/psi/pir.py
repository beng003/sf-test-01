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


# todo:隐匿查询封装
spu.pir_setup(
    server="alice",
    input_path=f"/mnt/users/beng003/sf-test/scr/data/alice/alice_psi.csv",
    key_columns=['uid'],
    label_columns=[
        "sepal length (cm)", "sepal width (cm)", "petal length (cm)"
    ],
    oprf_key_path=
    f"/mnt/users/beng003/sf-test/scr/data/configuration/alice_oprf_key.bin",
    setup_path=f"/mnt/users/beng003/sf-test/scr/data/alice/alice_setup",
    num_per_query=1,
    label_max_len=20,
    bucket_size=1000000,
)

spu.pir_query(
    server="alice",
    client="bob",
    server_setup_path=f"/mnt/users/beng003/sf-test/scr/data/alice/alice_setup",
    client_key_columns=["uid"],
    client_input_path=f"/mnt/users/beng003/sf-test/scr/data/bob/bob_psi.csv",
    client_output_path=
    f"/mnt/users/beng003/sf-test/scr/data/bob/bob_pir_result.csv",
)

sf.shutdown()
