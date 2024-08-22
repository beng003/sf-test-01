import secretflow as sf

# Check the version of your SecretFlow
print("The version of SecretFlow: {}".format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

sf.init(["alice", "bob"], address="local")
spu_config = sf.utils.testing.cluster_def(parties=["alice", "bob"])
spu_device = sf.SPU(spu_config)
alice, bob = sf.PYU("alice"), sf.PYU("bob")

print("***************************************************** PSI")

input_path = {
    alice: "/mnt/users/beng003/sf-test/data/v_alice.csv",
    bob: "/mnt/users/beng003/sf-test/data/v_bob.csv",
}
output_path = {
    alice: "/mnt/users/beng003/sf-test/data/alice_psi.csv",
    bob: "/mnt/users/beng003/sf-test/data/bob_psi.csv",
}

spu_device.psi_csv("uid", input_path, output_path, "alice")

# from secretflow.data.vertical import read_csv as v_read_csv

# vdf = v_read_csv(input_path, spu=spu_device, keys="uid", drop_keys="uid")
# print("*****************************************************Alice PSI")
# vdf.to_csv(output_path, index=False)

from secretflow.data.core import partition
from secretflow.data.core.io import read_csv_wrapper
from typing import Callable, Dict, List, Union
from secretflow.device import PYU, SPU, Device
from secretflow.utils.errors import InvalidArgumentError
from secretflow.utils.random import global_random
from secretflow.data.vertical.dataframe import VDataFrame


def get_keys(
    device: Device, x: Union[str, List[str], Dict[Device, List[str]]] = None
) -> List[str]:
    if x:
        if isinstance(x, str):
            return [x]
        elif isinstance(x, List):
            return x
        elif isinstance(x, Dict):
            if device in x:
                if isinstance(x[device], str):
                    return [x[device]]
                else:
                    return x[device]
        else:
            raise InvalidArgumentError(f"Illegal type for keys,got {type(x)}")
    else:
        return []


filepath_actual = output_path

# note:默认可以不设置的参数都
converters = None
dtypes = None
usecols = None
no_header = False
backend = "pandas"
delimiter = ","
nrows: int = None
skip_rows_after_header: int = None
keys = "uid"
drop_keys = "uid"

partitions = {}
for device, path in filepath_actual.items():
    converter = converters[device] if converters is not None else None
    dtype = dtypes[device] if dtypes is not None else None
    usecol = usecols[device] if usecols is not None else None

    if usecol is None and dtype is not None:
        usecol = dtype.keys()

    if no_header:
        assert usecol is None, "can not use usecol when no_header is True"

    partitions[device] = partition(
        data=read_csv_wrapper,
        device=device,
        backend=backend,
        filepath=path,
        auto_gen_header_prefix=str(device) if no_header else "",
        delimiter=delimiter,
        usecols=usecol,
        dtype=dtype,
        converters=converter,
        read_backend=backend,
        nrows=nrows,
        skip_rows_after_header=skip_rows_after_header,
    )
if drop_keys:
    for device, part in partitions.items():
        device_drop_key = get_keys(device, drop_keys)
        device_psi_key = get_keys(device, keys)

        if device_drop_key is not None:
            columns_set = set(part.columns)
            device_drop_key_set = set(device_drop_key)
            assert columns_set.issuperset(device_drop_key_set), (
                f"drop_keys = {device_drop_key_set.difference(columns_set)}"
                " can not find on device {device}"
            )

            device_psi_key_set = set(device_psi_key)
            assert device_psi_key_set.issuperset(device_drop_key_set), (
                f"drop_keys = {device_drop_key_set.difference(device_psi_key_set)} "
                f"can not find on device_psi_key_set of device {device},"
                f" which are {device_psi_key_set}"
            )

            partitions[device] = part.drop(columns=device_drop_key)

unique_cols = set()

# data columns must be unique across all devices
if len(partitions):
    parties_length = {}
    for device, part in partitions.items():
        parties_length[device.party] = len(part)
    if len(set(parties_length.values())) > 1:
        raise AssertionError(
            f"number of samples must be equal across all devices, got {parties_length}, "
            f"input uri {filepath_actual}"
        )

for device, part in partitions.items():
    for col in part.columns:
        assert col not in unique_cols, f"col {col} duplicate in multiple devices"
        unique_cols.add(col)

vdf = VDataFrame(partitions)

print("**********Alice PSI")
print(vdf)
print(vdf.shape)
print(sf.reveal(vdf))

sf.shutdown()
