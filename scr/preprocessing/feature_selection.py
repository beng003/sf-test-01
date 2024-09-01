from secretflow.data.horizontal import HDataFrame
from secretflow.data.vertical import VDataFrame
from typing import Union
import pandas as pd
from scr.preprocessing import *
import secretflow as sf
from secretflow.device import SPUObject
import numpy as np
import pandas as pd


def by_missing(
    df: Union[
        HDataFrame,
        VDataFrame,
    ],
    threshold=0.3,
) -> Union[HDataFrame, VDataFrame, None]:
    """
    根据缺失值比例进行特征选择，删除缺失值比例超过指定阈值的列。

    参数:
        df: 可以是水平分区 (HDataFrame) 或垂直分区 (VDataFrame) 的数据集。
        threshold: 缺失值比例的阈值，超过该阈值的列将被删除，默认为 0.3 (30%)。

    返回值:
        处理后的 HDataFrame 或 VDataFrame，删除了缺失值比例超过阈值的列。如果没有列被删除或 df 为 None，返回 None。
    
    功能说明:
        该函数会计算数据集中每列的缺失值比例，并将缺失值比例大于指定阈值的列从数据集中删除。
        删除操作并不会改变原始数据集，而是返回一个新的数据集。
    """
    # 计算每列缺失值的比例
    missing_ratios = df.isna().mean()
    columns_to_drop = [
        col for col in df.columns if missing_ratios[col] > threshold
    ]

    # 删除缺失值比例超过阈值的列
    for col in columns_to_drop:
        ndf = df.drop(columns=col, axis=1, inplace=False)

    return ndf


def hvar(
    df: HDataFrame,
    spu_device: SPUObject,
) -> pd.Series:
    """
    计算给定 HDataFrame 中每一列的方差。该函数考虑数据被分区存储，并通过安全多方计算设备（SPU）进行计算。

    参数:
        df (HDataFrame): 分区存储的数据框，每个分区存储 HDataFrame 的一部分。
        spu_device (SPUObject): 用于执行分布式安全计算的设备。

    返回:
        pd.Series: 包含每一列方差的 pandas Series 对象。

    内部函数:
        squared_deviation_sum(df, df_means) -> pd.Series:
            计算每一列数据与其均值之间的差的平方和。

    逻辑流程:
        1. 计算每一列的均值。
        2. 对于每一列，初始化方差累加器 `column_sum` 和计数器 `cnts`。
        3. 对每个分区的数据，计算该分区中的差平方和并累加到 `column_sum` 中。
        4. 通过 SPU 设备计算方差，并区分样本方差与总体方差（减去1的修正项）。
        5. 返回每列的方差值。
    """

    def squared_deviation_sum(df, df_means) -> pd.Series:
        """
        计算给定数据框的每一项减去均值后的平方和。

        参数:
            df (HDataFrame): 数据框。
            df_means (pd.Series): 每列数据的均值。

        返回:
            pd.Series: 每列的平方和。
        """
        # 计算每一项减去均值后的平方
        squared_deviations = (df - df_means)**2

        # 计算每列的平方和
        squared_deviation_sum = squared_deviations.sum()

        return squared_deviation_sum

    df_means = df.mean()
    column_sum = {}
    cnts = {}
    for column in df.columns:
        column_sum[column] = spu_device(lambda x: x)(0)
        cnts[column] = spu_device(lambda x: x)(df[column].count()[column])
        for part in df.partitions.values():
            # 计算差的平方和
            squared_differences = part.device(squared_deviation_sum)(
                part[column].data,
                df_means[column],
            ).to(spu_device)

            # 计算平方和
            column_sum[column] = spu_device(lambda x, y: x + y)(
                column_sum[column], squared_differences)

    # hack:考虑样本方差和总体方差区别
    return pd.Series(
        [
            float(a[0]) for a in sf.reveal([
                spu_device(lambda x, y: x / (y - 1))
                (column_sum[column], cnts[column]) for column in df.columns
            ])
        ],
        index=df.columns,
        dtype=np.float64,
    )


def hstd(
    df: HDataFrame,
    spu_device: SPUObject,
) -> pd.Series:
    """
    计算给定 HDataFrame 中每一列的标准差。

    参数:
        df (HDataFrame): 分区存储的数据框，每个分区存储 HDataFrame 的一部分。
        spu_device (SPUObject): 用于执行分布式安全计算的设备。

    返回:
        pd.Series: 包含每一列标准差的 pandas Series 对象。

    逻辑流程:
        1. 调用 `hvar` 函数计算方差。
        2. 对方差取平方根得到标准差。
    """
    return hvar(df, spu_device).apply(np.sqrt)


def by_cv(
    df: Union[
        HDataFrame,
        VDataFrame,
    ],
    threshold: float = 0.1,
    spu_device: SPUObject = None,
) -> Union[HDataFrame, VDataFrame]:
    """
    根据变异系数（Coefficient of Variation, CV）进行特征选择。

    Args:
        df (pd.DataFrame): 包含特征的 DataFrame。
        threshold (float): 变异系数阈值，低于此阈值的特征将被删除。

    Returns:
        pd.DataFrame: 删除了低变异系数特征的 DataFrame。
    """
    if isinstance(df, VDataFrame):
        std = df.std()
    elif isinstance(df, HDataFrame) and spu_device is not None:
        std = hstd(df, spu_device)
    else:
        raise ValueError("Unsupported data type or SPU device not provided.")

    # 计算每个特征的均值和标准差
    mean = df.mean()

    # 计算变异系数
    cv = std / mean

    # 选择变异系数大于阈值的特征
    selected_columns = cv[cv > threshold].index

    # 返回过滤后的数据集
    return df[selected_columns]
