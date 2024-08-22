import importlib
import sys
import yaml
import numpy as np
from secretflow import DeviceObject

def import_from_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_yaml(target):
    # if isinstance(target, str) or isinstance(target, bytes):
    #     return yaml.load(target, Loader=yaml.FullLoader)
    with open(target, encoding="utf-8") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)


def write_yaml(target, data):
    """
    将数据写入到指定的 YAML 文件中。

    参数:
    - target: 目标文件路径
    - data: 要写入的数据对象
    """
    with open(target, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)


def device_get_data(device: DeviceObject, data: np.ndarray):
    """
    从 SecretFlow 设备获取数据。

    此函数通过指定的设备对象，将数据从设备中提取到本地。它利用设备对象的调用功能来访问存储在设备上的数据。

    Args:
        device (DeviceObject): 设备对象，用于从中提取数据的设备。该设备对象应能够处理数据的检索操作。
        data (np.ndarray): 存储在设备上的数据。此数据应该是 NumPy 数组类型，以便与设备对象兼容。

    Returns:
        The result of the device's data retrieval operation. The exact type and structure of the returned data depend on the device's implementation.
        The returned data will be the same type as the `data` argument, typically a NumPy array.

    Example:
        >>> device = DeviceObject(...)  # 设备初始化
        >>> data = np.array([1, 2, 3])   # 示例数据
        >>> result = device_get_data(device, data)
        >>> print(result)
        [1, 2, 3]  # 示例输出，具体输出取决于设备和数据

    Notes:
        - Ensure that the `device` object is properly initialized and capable of handling the `data`.
        - The function assumes that the `device` object can be called with a function that takes `data` as its input.
    """
    assert isinstance(
        data, (int, float, np.ndarray)
    ), f"Expected data to be of type int, float or np.ndarray, but got {type(data).__name__}."

    def get_data(x):
        return x

    return device(get_data)(data)


