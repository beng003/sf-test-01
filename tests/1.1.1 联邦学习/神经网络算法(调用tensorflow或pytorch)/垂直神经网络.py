# https://www.secretflow.org.cn/zh-CN/docs/secretflow/v1.8.0b0/tutorial/SL_Training_with_compressor#%E4%BD%BF%E7%94%A8%E9%80%9A%E8%AE%AF%E5%8E%8B%E7%BC%A9%E7%AE%97%E6%B3%95

import secretflow as sf
import matplotlib.pyplot as plt

sf.shutdown()
sf.init(['alice', 'bob'], address='local')
alice, bob = sf.PYU('alice'), sf.PYU('bob')

from secretflow.utils.simulation.datasets import load_bank_marketing
from secretflow.preprocessing.scaler import MinMaxScaler
from secretflow.preprocessing.encoder import LabelEncoder
from secretflow.data.split import train_test_split

random_state = 1234

data = load_bank_marketing(parts={alice: (0, 4), bob: (4, 16)}, axis=1)
label = load_bank_marketing(parts={alice: (16, 17)}, axis=1)

encoder = LabelEncoder()
data['job'] = encoder.fit_transform(data['job'])
data['marital'] = encoder.fit_transform(data['marital'])
data['education'] = encoder.fit_transform(data['education'])
data['default'] = encoder.fit_transform(data['default'])
data['housing'] = encoder.fit_transform(data['housing'])
data['loan'] = encoder.fit_transform(data['loan'])
data['contact'] = encoder.fit_transform(data['contact'])
data['poutcome'] = encoder.fit_transform(data['poutcome'])
data['month'] = encoder.fit_transform(data['month'])
label = encoder.fit_transform(label)

scaler = MinMaxScaler()
data = scaler.fit_transform(data)

train_data, test_data = train_test_split(data,
                                         train_size=0.8,
                                         random_state=random_state)
train_label, test_label = train_test_split(label,
                                           train_size=0.8,
                                           random_state=random_state)


def create_base_model(input_dim, output_dim, name='base_model'):
    # Create model
    def create_model():
        from tensorflow import keras
        from tensorflow.keras import layers
        import tensorflow as tf

        model = keras.Sequential([
            keras.Input(shape=input_dim),
            layers.Dense(100, activation="relu"),
            layers.Dense(output_dim, activation="relu"),
        ])
        # Compile model
        model.summary()
        model.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=["accuracy", tf.keras.metrics.AUC()],
        )
        return model

    return create_model


# prepare model
hidden_size = 64

model_base_alice = create_base_model(4, hidden_size)
model_base_bob = create_base_model(12, hidden_size)


def create_fuse_model(input_dim, output_dim, party_nums, name='fuse_model'):

    def create_model():
        from tensorflow import keras
        from tensorflow.keras import layers
        import tensorflow as tf

        # input
        input_layers = []
        for i in range(party_nums):
            input_layers.append(keras.Input(input_dim, ))

        merged_layer = layers.concatenate(input_layers)
        fuse_layer = layers.Dense(64, activation='relu')(merged_layer)
        output = layers.Dense(output_dim, activation='sigmoid')(fuse_layer)

        model = keras.Model(inputs=input_layers, outputs=output)
        model.summary()

        model.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=["accuracy", tf.keras.metrics.AUC()],
        )
        return model

    return create_model


model_fuse = create_fuse_model(input_dim=hidden_size,
                               party_nums=2,
                               output_dim=1)

base_model_dict = {alice: model_base_alice, bob: model_base_bob}

from secretflow.ml.nn import SLModel

sl_model_origin = SLModel(
    base_model_dict=base_model_dict,
    device_y=alice,
    model_fuse=model_fuse,
)

from secretflow.utils.compressor import QuantizedCompressor
from secretflow.utils.compressor.quantized_compressor import QuantizedCompressedData
import numpy as np


class QuantizedKmeans(QuantizedCompressor):
    """Quantized compressor with Kmeans, a algorithm which replace float with relatived centroid's index.

    Reference paper 2016 "Deep Compression: Compressing Deep Neural Networks with Pruning, Trained Quantization and Huffman Coding".

    Link: https://arxiv.org/abs/1510.00149
    """

    class KmeansCompressData(QuantizedCompressedData):

        def __init__(self,
                     compressed_data,
                     quant_bits,
                     origin_type=None,
                     q=None):
            super().__init__(compressed_data, quant_bits, origin_type)
            self.q = q

    def __init__(self, quant_bits: int = 8, n_clusters=None):
        super().__init__(quant_bits)
        from sklearn.cluster import KMeans

        if n_clusters is None:
            self.n_clusters = quant_bits
        else:
            self.n_clusters = n_clusters
        self.km = KMeans(self.n_clusters, n_init=1, max_iter=50)

    def _compress_one(self, data: np.ndarray,
                      **kwargs) -> "KmeansCompressData":
        if data.flatten().shape[0] <= self.n_clusters:
            return self.KmeansCompressData(data, self.quant_bits)
        ori_shape = data.shape
        self.km.fit(np.expand_dims(data.flatten(), axis=1))

        quantized = self.km.labels_ - (1 << (self.quant_bits - 1))

        quantized = np.reshape(quantized, ori_shape)
        q = self.km.cluster_centers_

        return self.KmeansCompressData(quantized.astype(self.np_type),
                                       self.quant_bits, data.dtype, q)

    def _decompress_one(self, data: "KmeansCompressData") -> np.ndarray:
        if data.compressed_data.flatten().shape[0] <= self.n_clusters:
            return data.compressed_data
        label = data.compressed_data.astype(
            data.origin_type) + (1 << (self.quant_bits - 1))
        dequantized = np.zeros_like(label)
        for i in range(data.q.shape[0]):
            dequantized[label == i] = data.q[i]

        return dequantized


qkm = QuantizedKmeans()

sl_model_kmeans = SLModel(
    base_model_dict=base_model_dict,
    device_y=alice,
    model_fuse=model_fuse,
    compressor=qkm,
)

history_kmeans = sl_model_kmeans.fit(
    train_data,
    train_label,
    validation_data=(test_data, test_label),
    epochs=5,
    batch_size=128,
    shuffle=True,
    verbose=1,
    validation_freq=1,
)

plt.plot(history_kmeans['train_auc_1'])
plt.plot(history_kmeans['val_auc_1'])

plt.title('Model Area Under Curve')
plt.ylabel('Area Under Curve')
plt.xlabel('Epoch')
plt.legend(['kmeans', 'kmeans_val'], loc='lower right')
plt.show()

sf.shutdown()
