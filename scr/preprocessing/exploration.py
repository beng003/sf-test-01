import pandas as pd
from typing import Union
from secretflow.data.horizontal import HDataFrame
from secretflow.data.vertical import VDataFrame

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
