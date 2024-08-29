from secretflow.preprocessing.encoder import OneHotEncoder as SecretFlowOneHotEncoder
from secretflow.preprocessing.encoder import VOrdinalEncoder as SecretFlowVOrdinalEncoder
from secretflow.preprocessing.encoder import LabelEncoder as SecretFlowLabelEncoder
from secretflow.preprocessing.binning.vert_woe_binning import VertWoeBinning as SecretVertWoeBinning
from secretflow.preprocessing.binning.vert_bin_substitution import VertBinSubstitution
from secretflow.device import HEU, PYU, SPU
from secretflow.data.horizontal import HDataFrame
from secretflow.data.mix import MixDataFrame
from secretflow.data.vertical import VDataFrame
from typing import Dict, List, Union
# from secretflow.preprocessing import SecretFlowOneHotEncoder

all = [
    "OneHotEncoder",
    "OrdinalEncoder",
    "LabelEncoder",
    "WOEEncoder",
]


def OneHotEncoder(
    df: Union[HDataFrame, VDataFrame, MixDataFrame],
    min_frequency=None,
    max_categories=None,
) -> Union[HDataFrame, VDataFrame, MixDataFrame]:
    """
    Apply One-Hot Encoding to the provided dataframe.

    Args:
        df (Union[HDataFrame, VDataFrame, MixDataFrame]): The input dataframe to encode.
        min_frequency (int or float, optional): Minimum frequency threshold for considering a category.
        max_categories (int, optional): Maximum number of categories to encode for each feature.

    Returns:
        Union[HDataFrame, VDataFrame, MixDataFrame]: The encoded dataframe.
    """
    onehot_encoder = SecretFlowOneHotEncoder(min_frequency, max_categories)
    onehot_target = onehot_encoder.fit_transform(df)
    return onehot_target


def OrdinalEncoder(
    df: Union[HDataFrame, VDataFrame], ) -> Union[HDataFrame, VDataFrame]:
    """
    # todo: HDataFrame数据顺序编码
    Apply Ordinal Encoding to the provided dataframe.

    Args:
        df (VDataFrame): The input dataframe to encode.

    Returns:
        VDataFrame: The encoded dataframe.
    """
    if not isinstance(df, VDataFrame):
        raise TypeError("Current input data must be of type VDataFrame.")

    ordinal_encoder = SecretFlowVOrdinalEncoder()
    ordinal_target = ordinal_encoder.fit_transform(df)
    return ordinal_target


def LabelEncoder(
    df: Union[HDataFrame, VDataFrame],
) -> Union[HDataFrame, VDataFrame, MixDataFrame]:
    """Fit label encoder and return encoded labels.

    Args:
        df (VDataFrame): The input dataframe to encode.

    Returns:
        VDataFrame: The encoded dataframe.
    """
    ordinal_encoder = SecretFlowLabelEncoder()
    ordinal_target = ordinal_encoder.fit_transform(df)
    return ordinal_target


def WOEEncoder(
    secure_device: Union[SPU, HEU],
    vdata: VDataFrame,
    binning_method: str = "quantile",
    bin_num: int = 10,
    bin_names: Dict[PYU, List[str]] = {},
    label_name: str = "",
    positive_label: str = "1",
    chimerge_init_bins: int = 100,
    chimerge_target_bins: int = 10,
    chimerge_target_pvalue: float = 0.1,
    audit_log_path: Dict[str, str] = {},
) -> VDataFrame:
    """
    # todo: HDataFrame WOE编码
    Apply Weight of Evidence (WOE) encoding to the provided vertical dataframe.

    This function performs the following steps:
    1. **Binning**: The data is first binned using the specified method. Binning methods include quantile-based binning or other methods.
    2. **WOE Encoding**: Weight of Evidence encoding is applied to transform the binned data.

    Args:
        secure_device (Union[SPU, HEU]): The secure computing device to use for privacy-preserving computations.
        vdata (VDataFrame): The input vertical dataframe to be encoded. It should contain the features to be binned and encoded.
        binning_method (str, optional): The method used for binning the data. Options include "quantile" for quantile-based binning. Defaults to "quantile".
        bin_num (int, optional): The number of bins to create for the continuous features. Defaults to 10.
        bin_names (Dict[PYU, List[str]], optional): A dictionary specifying custom bin names for each party. Defaults to an empty dictionary.
        label_name (str, optional): The name of the label column used for calculating WOE. Defaults to an empty string.
        positive_label (str, optional): The label value representing the positive class. Defaults to "1".
        chimerge_init_bins (int, optional): The initial number of bins for the ChiMerge algorithm, used for merging bins. Defaults to 100.
        chimerge_target_bins (int, optional): The target number of bins after merging. Defaults to 10.
        chimerge_target_pvalue (float, optional): The p-value threshold for merging bins in the ChiMerge algorithm. Defaults to 0.1.
        audit_log_path (Dict[str, str], optional): A dictionary specifying paths for logging audit information during the binning process. Defaults to an empty dictionary.

    Returns:
        VDataFrame: The dataframe with WOE encoding applied. The output dataframe contains the transformed features with WOE values.
    """
    binning = SecretVertWoeBinning(secure_device)

    bin_rules = binning.binning(
        vdata,
        binning_method,
        bin_num,
        bin_names,
        label_name,
        positive_label,
        chimerge_init_bins,
        chimerge_target_bins,
        chimerge_target_pvalue,
        audit_log_path,
    )

    woe_sub = VertBinSubstitution()
    sub_data = woe_sub.substitution(vdata, bin_rules)
    return sub_data[0]
