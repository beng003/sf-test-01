from secretflow.preprocessing import MinMaxScaler as SecretFlowMinMaxScaler
from secretflow.preprocessing import StandardScaler as SecretFlowStandardScaler
from secretflow.data.horizontal import HDataFrame
from secretflow.data.vertical import VDataFrame
from secretflow.data.mix.dataframe import MixDataFrame
from typing import Union
from secretflow.security.aggregation import SecureAggregator


def MinMaxScaler(
    df: Union[HDataFrame, VDataFrame, MixDataFrame]
) -> Union[HDataFrame, VDataFrame, MixDataFrame]:
    """Fit the MinMaxScaler and transform the data.
    
    # fixme:(ActorPartitionAgent pid=1408122) /mnt/users/beng003/anaconda3/envs/sf/lib/python3.10/site-packages/sklearn/base.py:458: UserWarning: X has feature names, but MinMaxScaler was fitted without feature names.
    
    Args:
        df: HDataFrame, VDataFrame, or MixDataFrame.
    
    Returns:
        The scaled dataframe.
    """
    # Create the SecretFlow MinMaxScaler instance
    scaler = SecretFlowMinMaxScaler()

    # Fit the scaler on the dataframe and transform it
    scaled_df = scaler.fit_transform(df)

    return scaled_df


def StandardScaler(
    df: Union[HDataFrame, VDataFrame, MixDataFrame],
    with_mean=True,
    with_std=True,
    aggregator: SecureAggregator = None,
) -> Union[HDataFrame, VDataFrame, MixDataFrame]:
    """Fit the StandardScaler and transform the data.

    This function standardizes the input dataframe by removing the mean and scaling
    to unit variance. The input can be horizontally or vertically partitioned,
    and the SecureAggregator is used to compute the global statistics for
    horizontally partitioned data.

    Args:
        df (HDataFrame, VDataFrame, MixDataFrame): 
            The federated dataframe to be standardized. It can be horizontally 
            partitioned (HDataFrame), vertically partitioned (VDataFrame), 
            or a mixed partition (MixDataFrame).
        with_mean (bool, optional): 
            Whether to center the data before scaling. Defaults to True.
        with_std (bool, optional): 
            Whether to scale the data to unit variance. Defaults to True.
        aggregator (SecureAggregator, optional): 
            The secure aggregator used for computing global mean and variance 
            for horizontally partitioned data. Required for horizontal MixDataFrame.

    Returns:
        Union[HDataFrame, VDataFrame, MixDataFrame]: 
            The standardized dataframe with the same structure as the input.
    """
    # 创建 SecretFlow 的 StandardScaler 实例
    scaler = SecretFlowStandardScaler(
        with_mean=with_mean,
        with_std=with_std,
    )

    # 拟合并转换数据
    scaled_df = scaler.fit_transform(df, aggregator=aggregator)

    return scaled_df
