from secretflow.preprocessing import KBinsDiscretizer as SecretFlowKBinsDiscretizer
from secretflow.data.horizontal import HDataFrame
from secretflow.data.vertical import VDataFrame
from secretflow.data.mix.dataframe import MixDataFrame
from typing import Union
from secretflow.security.aggregation import Aggregator
from secretflow.security.compare import Comparator


def KBinsDiscretizer(
    df: Union[HDataFrame, VDataFrame, MixDataFrame],
    n_bins=5,
    strategy: str = 'quantile',
    aggregator: Aggregator = None,
    comparator: Comparator = None,
    compress_thres: int = 10000,
    error: float = 1e04,
    max_iter: int = 200,
) -> Union[HDataFrame, VDataFrame, MixDataFrame]:
    """Fit the estimator.

    Args:
        df: the X to fit.
        n_bins: The number of bins to produce.
        strategy: {'uniform', 'quantile'}, notice that 'kmeans' is not supported yet now.
        aggregator: optional; shall be provided if df is a horizontal partitioned MixDataFrame.
        comparator: optional; shall be provided if df is a horizontal partitioned MixDataFrame.
        compress_thres: optional; the compress threshold of :py:class:`~secretflow.preprocessing.binning.homo_binning.HomoBinning`.
        error: optional; the error of :py:class:`~secretflow.preprocessing.binning.homo_binning.HomoBinning`.
        max_iter: optional; the max iterations of :py:class:`~secretflow.preprocessing.binning.homo_binning.HomoBinning`.

    Returns:
        the transformed X in federated dataframe.
        """
    estimator = SecretFlowKBinsDiscretizer(n_bins=n_bins, strategy=strategy)
    binned = estimator.fit_transform(
        df,
        aggregator=aggregator,
        comparator=comparator,
        compress_thres=compress_thres,
        error=error,
        max_iter=max_iter,
    )

    return binned
