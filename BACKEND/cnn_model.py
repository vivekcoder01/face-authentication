import tensorflow as tf
from tensorflow.keras.models import load_model

# Lightweight CNN (FaceNet-style embedding model)
def load_cnn_model():
    model = tf.keras.applications.MobileNetV2(
        input_shape=(160, 160, 3),
        include_top=False,
        pooling='avg',
        weights='imagenet'
    )
    return model
