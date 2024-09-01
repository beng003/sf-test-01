import numpy as np
import pandas as pd

data = {
    'feature_1': [1, 2, 3, 4, 5],
    'feature_2': [10, 10, 10, 10, 10],  # 变异系数为 0
    'feature_3': [100, 200, 300, 400, 500],  # 较大的变异系数
}
data = pd.DataFrame(data)
column_sum = pd.Series(
    np.zeros(len(data.columns)),
    index=data.columns,
)
column_sum['feature_1'] = [1, 1, 1, 1, 1]
print(column_sum)
