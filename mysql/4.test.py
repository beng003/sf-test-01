from read_mysql import read_mysql as rm

import secretflow as sf

# Check the version of your SecretFlow
print("The version of SecretFlow: {}".format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(["alice", "bob"], address="local")
spu_config = sf.utils.testing.cluster_def(parties=["alice", "bob"])
spu_device = sf.SPU(spu_config)
alice, bob = sf.PYU("alice"), sf.PYU("bob")

filepath = {
    alice: {"database_name": "alice_database", "table_name": "alice_iris"},
    bob: {"database_name": "bob_database", "table_name": "bob_iris"},
}

vdf = rm(filepath, spu_device, keys='uid', drop_keys = 'uid')

print(vdf)
sf.shutdown()
