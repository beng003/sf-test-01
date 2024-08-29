from secretflow.component.preprocessing.filter.sample import SampleAlgorithmFactory
from secretflow.data.vertical import VDataFrame
from secretflow.data.horizontal import HDataFrame


def vdf_sample(
    input_df: VDataFrame,
    total_num: int,
    sample_algorithm: str = "random",
    random_frac: float = 0.8,
    random_random_state: int = 42,
    random_replacement: bool = False,
    system_frac: float = None,
    stratify_frac: float = None,
    stratify_random_state: int = None,
    stratify_observe_feature: str = None,
    stratify_replacements: list[bool] = None,
    quantiles: list[float] = None,
    weights: list[float] = None,
):
    """
    # xxx:目前没有HDataFrame数据的抽样方法
    # todo: HDataFrame数据的抽样方法,参考/mnt/users/beng003/anaconda3/envs/sf/lib/python3.10/site-packages/secretflow/component/preprocessing/filter/sample.py中的SampleAlgorithm类的perform_sample方法
    Creates and returns an instance of a sampling algorithm class based on the specified sampling method.

    Parameters:
    -----------
    input_df : VDataFrame
        Input dataset to be sampled from, represented as a custom VDataFrame.
    total_num : int
        The total number of samples to be drawn from the dataset.
    sample_algorithm : str
        The sampling method to be used. Valid options are:
        - RANDOM_SAMPLE("random") : Random sampling algorithm.
        - SYSTEM_SAMPLE("system"): Systematic sampling algorithm.
        - STRATIFY_SAMPLE("stratify") : Stratified sampling algorithm.
    random_frac : float
        Fraction of data to be sampled using the random sampling algorithm (applicable for RANDOM_SAMPLE).
    random_random_state : int
        Seed value for the random number generator to ensure reproducibility of random sampling (applicable for RANDOM_SAMPLE).
    random_replacement : bool
        Indicates whether sampling with replacement should be performed in random sampling (True for with-replacement, False for without-replacement).
    system_frac : float
        Fraction of data to be sampled using the systematic sampling algorithm (applicable for SYSTEM_SAMPLE).
    stratify_frac : float
        Fraction of data to be sampled from each stratum in stratified sampling (applicable for STRATIFY_SAMPLE).
    stratify_random_state : int
        Seed value for the random number generator to ensure reproducibility in stratified sampling (applicable for STRATIFY_SAMPLE).
    stratify_observe_feature : str
        The column name to be used as the observation feature for stratification (applicable for STRATIFY_SAMPLE).
    stratify_replacements : list[bool]
        A list of booleans specifying whether replacement should be used in each stratum for stratified sampling (applicable for STRATIFY_SAMPLE).
    quantiles : list[float]
        Quantiles used to define the boundaries of the strata for stratified sampling (applicable for STRATIFY_SAMPLE).
    weights : list[float]
        Weights associated with each stratum in stratified sampling to control the proportion of samples drawn from each stratum (applicable for STRATIFY_SAMPLE).

    Returns:
    --------
    object
        An instance of the appropriate sampling algorithm class, initialized with the provided parameters.

    Raises:
    -------
    AssertionError
        If the `sample_algorithm` parameter is not one of the valid options: RANDOM_SAMPLE, SYSTEM_SAMPLE, or STRATIFY_SAMPLE.
    """

    sample_algorithm_obj = SampleAlgorithmFactory().create_sample_algorithm(
        input_df=input_df,
        total_num=total_num,
        sample_algorithm=sample_algorithm,
        random_frac=random_frac,
        random_random_state=random_random_state,
        random_replacement=random_replacement,
        system_frac=system_frac,
        stratify_frac=stratify_frac,
        stratify_random_state=stratify_random_state,
        stratify_observe_feature=stratify_observe_feature,
        stratify_replacements=stratify_replacements,
        quantiles=quantiles,
        weights=weights,
    )

    # 执行抽样
    sample_df, report_results = sample_algorithm_obj.perform_sample()
    return sample_df, report_results


def hdf_sample(
    input_df: HDataFrame,
    total_num: int,
    sample_algorithm: str = "random",
    random_frac: float = 0.8,
    random_random_state: int = 42,
    random_replacement: bool = False,
    system_frac: float = None,
    stratify_frac: float = None,
    stratify_random_state: int = None,
    stratify_observe_feature: str = None,
    stratify_replacements: list[bool] = None,
    quantiles: list[float] = None,
    weights: list[float] = None,
):
    """
    # todo: HDataFrame数据的抽样方法,参考/mnt/users/beng003/anaconda3/envs/sf/lib/python3.10/site-packages/secretflow/component/preprocessing/filter/sample.py中的SampleAlgorithm类的perform_sample方法,参考/mnt/users/beng003/anaconda3/envs/sf/lib/python3.10/site-packages/secretflow/utils/simulation/data/dataframe.py的create_df
    Creates and returns an instance of a sampling algorithm class based on the specified sampling method.
    """
    raise NotImplementedError()
