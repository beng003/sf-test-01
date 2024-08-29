import numpy as np
import pandas as pd
from typing import Union
from secretflow.data.horizontal import HDataFrame
from secretflow.data.vertical import VDataFrame


# todo: 考虑明文实现转密文实现
def outlier_handler(data, dtype="numpy"):
    """
    该函数通过使用均值和标准差来计算数据的上下界，处理数据中的异常值（即远离大多数数据的极端值）。对于异常值，函数会用特定范围内的最大值或最小值进行替换，而不是直接删除或忽略它们。这种方法有助于保持数据的完整性，同时减轻异常值对分析或模型的影响。
    """
    if dtype == "numpy":
        data = pd.DataFrame(data)
    elif dtype != "pandas":
        raise TypeError(
            "No supported data type, please change data type to numpy or pandas!"
        )

    data = data.replace(np.inf, np.nan)
    for feature in data:
        top = data[feature].mean() + 2 * data[feature].std()
        bottom = data[feature].mean() - 2 * data[feature].std()
        rep_max = data[data[feature] < top][feature].max()
        data.loc[data[feature] > top, feature] = rep_max
        rep_min = data[data[feature] > bottom][feature].min()
        data.loc[data[feature] < bottom, feature] = rep_min
    return data


# todo: 考虑明文实现转密文实现
def miss_value_handler(data, handler="drop", dtype="numpy"):
    if dtype == "numpy":
        data = pd.DataFrame(data)
    elif dtype != "pandas":
        raise ValueError(
            "No supported data type, please change data type to numpy or pandas!"
        )

    data = data.replace(np.inf, np.nan)
    data.isnull().sum()

    if handler == "drop":
        data = data.dropna()
    elif handler == "mean":
        for feature in data:
            data[feature] = data[feature].fillna(data[feature].mean())
    elif handler == "interpolate":
        for feature in data:
            data[feature] = data[feature].fillna(data[feature].interpolate())
    else:
        for feature in data:
            data[feature] = data[feature].fillna(handler)

    if dtype == "numpy":
        data = np.array(data)
    return data


def table_statistics_vh(
        table: Union[pd.DataFrame, VDataFrame, HDataFrame]) -> pd.DataFrame:
    """
    Get table statistics for a pd.DataFrame, VDataFrame or HDataFrame.

    Args:
        table: Union[pd.DataFrame, VDataFrame, HDataFrame]
    Returns:
    """
    # todo: 数据探查功能添加
    assert isinstance(table, (
        pd.DataFrame, VDataFrame,
        HDataFrame)), f"table must be a pd.DataFrame, VDataFrame or HDataFrame"
    index = table.columns
    result = pd.DataFrame(index=index)
    result["datatype"] = table.dtypes
    result["total_count"] = table.shape[0]
    result["count(non-NA count)"] = table.count()
    result["count_na(NA count)"] = table.isna().sum()
    result["na_ratio"] = table.isna().sum() / table.shape[0]
    result["min"] = table.min(numeric_only=True)
    result["max"] = table.max(numeric_only=True)
    result["mean"] = table.mean(numeric_only=True)

    result["sum"] = table.sum(numeric_only=True)

    return result
