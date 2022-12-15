import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import geopandas as gpd
import tensorflow as tf
from tensorflow import keras

from sklearn.model_selection import train_test_split

class Estimator:
    def __init__(self):
        self.model = keras.models.Sequential([
                        keras.layers.LSTM(20, return_sequences=True, input_shape=[None, 1]),
                        keras.layers.LSTM(20, return_sequences=True),
                        keras.layers.Dense(1)
                ])
        self.model.compile(loss="mse", optimizer="adam")
        
    def set_train(self, df, interval=1, window_size = 10):
        """
        set the training data for prediction
        Args:
            df (DataFrame): dataframe
            interval (int, optional): interval in minutes. Defaults to 1.
            windows_size: window size
        """
        # df = df[df["id_area"] == self.area_id]
        df = df.sort_values(by="timestamp")
        areas_id = df["id_area"].unique()
        for id in areas_id:
            grouped_df=df.loc[df['id_area'] == id].groupby(pd.to_datetime(df["timestamp"]).dt.floor(str(interval)+"T"))["x"].count()
        grouped_df = grouped_df.tolist()
        X = []
        Y = []
        for i in range(0, len(grouped_df)-window_size-1):
            X.append([grouped_df[i:i+window_size]])
            Y.append(grouped_df[i+window_size+1])
        self.X = np.array(X).reshape(len(X), window_size)
        self.Y = np.array(Y)
    
    def split(self, X, Y, size = 0.1):
        X = X[:,:, np.newaxis]
        return train_test_split(X, Y, test_size=size)
    
    def fit(self):
        X_train, X_test, Y_train, Y_test = self.split(self.X, self.Y)
        self.history = self.model.fit(X_train, Y_train, epochs=20, validation_split=0.1)
        self.print_history()
        
        test_res = self.model.evaluate(X_test, Y_test)
        print(f"evaluation score: {test_res}") 
        
    def plot(self, data):
        plt.plot(data)
        plt.show()
        
    def print_history(self):
        plt.plot(self.history.history['loss'])
        plt.plot(self.history.history['val_loss'])
        plt.title('model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['train', 'valid'])
        plt.show()
    def load_model(self):
        """
        we load an old pretrained model
        """
        pass