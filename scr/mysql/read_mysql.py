from secretflow.data.core import partition
from typing import Callable, Dict, List, Union
from secretflow.device import PYU, SPU, Device
from secretflow.utils.errors import InvalidArgumentError
from secretflow.data.vertical.dataframe import VDataFrame
import pymysql
import pandas as pd


def read_mysql(
    filepath: Dict[PYU, dict],
    spu: SPU,
    delimiter=",",
    usecols: Dict[PYU, List[str]] = None,
    dtypes: Dict[PYU, Dict[str, type]] = None,
    converters: Dict[PYU, Dict[str, Callable]] = None,
    keys: Union[str, List[str], Dict[Device, List[str]]] = None,
    drop_keys: Union[str, List[str], Dict[Device, List[str]]] = None,
    psi_protocl=None,
    no_header: bool = False,
    backend: str = "pandas",
    nrows: int = None,
    skip_rows_after_header: int = None,
) -> VDataFrame:

    assert spu is not None, f"spu should not be None"
    if spu is not None:
        assert len(filepath) <= 3, f"only support 2 or 3 parties for now"

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

    def connect_to_mysql_and_read_data(
        database_name, table_name, host="localhost", user="beng003", password="12341234"
    ):
        connection = None
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database_name,
            )

            with connection.cursor() as cursor:

                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

            return pd.DataFrame(rows, columns=columns)

        except pymysql.MySQLError as e:
            print("错误：", e)
        finally:
            if connection:
                connection.close()

    if spu is not None:
        if psi_protocl is None:
            psi_protocl = "KKRT_PSI_2PC" if len(filepath) == 2 else "ECDH_PSI_3PC"

        v_data = []
        for pyu_i, param in filepath.items():
            v_data.append(pyu_i(connect_to_mysql_and_read_data)(**param))

        ab_psi = spu.psi_df(
            key=keys,
            dfs=v_data,
            protocol=psi_protocl,
            receiver=list(filepath.keys())[0].party,
        )

    partitions = {}
    for device_pyu in ab_psi:
        converter = converters[device_pyu.device] if converters is not None else None
        dtype = dtypes[device_pyu.device] if dtypes is not None else None
        usecol = usecols[device_pyu.device] if usecols is not None else None

        if usecol is None and dtype is not None:
            usecol = dtype.keys()

        if no_header:
            assert usecol is None, "can not use usecol when no_header is True"

        partitions[device_pyu.device] = partition(
            data=device_pyu,
            device=device_pyu.device,
            backend=backend,
            filepath="",
            auto_gen_header_prefix=str(device_pyu.device) if no_header else "",
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
                # f"input uri {filepath_actual}"
            )

    for device, part in partitions.items():
        for col in part.columns:
            assert col not in unique_cols, f"col {col} duplicate in multiple devices"
            unique_cols.add(col)

    return VDataFrame(partitions)
