import numpy as np
from secretflow import DeviceObject
import secretflow as sf
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from .log import *
from .path import *
from .tools import *


def sf_init_cluster(
    address: Optional[str] = None,
    cluster_config: Dict = None,
    tls_config: Dict[str, Dict] = None,
    parties: List[str] = None,
    **kwargs
):
    """
    初始化集群，并根据提供的配置设置 SecretFlow 的环境。

    Args:
        address (Optional[str], optional): Redis 服务器的地址，格式为 "host:port"。如果未提供，默认值为 "ecm-01:6379"。
        cluster_config (Dict, optional): 集群配置，包含集群各节点的配置信息。默认为从配置文件中读取。
        tls_config (Dict[str, Dict], optional): TLS 配置，包含每个节点的安全通信设置。默认为从配置文件中读取。
        parties (List[str], optional): 集群中的参与方列表，如 ["alice", "bob"]。如果未提供，默认使用 ["alice", "bob"]。

    Returns:
        Generator: 返回一个生成器，每个元素是初始化后的 SecretFlow PYU 对象，表示参与方。

    Raises:
        FileNotFoundError: 如果指定的配置文件路径不存在时，可能会抛出该异常。

    Example:
        >>> pyu_objects = init_cluster()
        >>> for pyu in pyu_objects:
        >>>     print(pyu)

    Notes:
        该函数假设配置文件路径由 PathManager 管理，并且已预先配置好。
    """
    path_manager = PathManager()
    CLUSTER_CONFIG_PATH = path_manager.get_path("CLUSTER_CONFIG_PATH")
    TLS_PATH = path_manager.get_path("TLS_PATH")

    address = "ecm-01:6379" if address is None else address
    cluster_config = (
        read_yaml(CLUSTER_CONFIG_PATH) if cluster_config is None else cluster_config
    )
    tls_config = read_yaml(TLS_PATH) if tls_config is None else tls_config
    parties = ["alice", "bob"] if parties is None else parties

    sf.init(
        address=address, cluster_config=cluster_config, tls_config=tls_config, **kwargs
    )

    return (sf.PYU(x) for x in parties)


def spu_init_cluster(cluster_def: Dict = None, link_desc: Dict = None, **kwargs):
    """
    初始化 SPU 设备集群。

    该函数用于初始化一个 SecretFlow (SPU) 设备集群，提供集群定义（`cluster_def`）和链路描述（`link_desc`）。若不提供这两个参数，将从指定的 YAML 配置文件中读取默认值。

    Args:
        cluster_def (Dict, optional): SPU 设备集群的配置字典。如果未提供，将从路径 `CLUSTER_DEF_PATH` 指定的 YAML 文件中加载配置。
        link_desc (Dict, optional): 用于描述设备间通信链路的配置字典。如果未提供，将从路径 `LINK_DESC_PATH` 指定的 YAML 文件中加载配置。
        **kwargs: 额外的关键字参数，传递给 SPU 设备的初始化函数，允许进行自定义配置。

    Returns:
        SPU: 一个初始化的 SPU 设备实例，用于执行集群操作。

    Raises:
        FileNotFoundError: 如果在路径中找不到所需的 YAML 配置文件。
        ValueError: 如果提供的配置文件格式不正确或无效。

    Example:
        spu_device = spu_init_cluster(cluster_def={"nodes": [...]}, link_desc={"protocol": "tcp"})
        # 使用初始化的 SPU 设备进行操作。
    """
    path_manager = PathManager()
    CLUSTER_DEF_PATH = path_manager.get_path("CLUSTER_DEF_PATH")
    LINK_DESC_PATH = path_manager.get_path("LINK_DESC_PATH")
    cluster_def = read_yaml(CLUSTER_DEF_PATH) if cluster_def is None else cluster_def
    link_desc = read_yaml(LINK_DESC_PATH) if link_desc is None else link_desc
    spu_device = sf.SPU(cluster_def=cluster_def, link_desc=link_desc, **kwargs)
    return spu_device
