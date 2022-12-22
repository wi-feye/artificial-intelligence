import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional, Dropout
from keras.callbacks import EarlyStopping

pm_vars_path = "./prediction_model_vars.json"

class Estimator:
    def __init__(self):
        
        self.model = None
        self.df = None
        self.window_size = None

        with open(pm_vars_path, "r") as file:
            vars = json.load(file)
            self.window_size = vars["window_size"]

        

    def split_series(self, dataset, n_past):
        #
        # n_past ==> no of past observations
        #
        X, y = list(), list()
        for elem in dataset:
            for window_start in range(len(elem)):
                past_end = window_start + n_past
                future_end = past_end + 1
                if future_end > len(elem):
                    break
                # slicing the past and future parts of the window
                past, future = elem[window_start:past_end], elem[past_end:future_end]
                X.append(past)
                y.append(future)
        return np.array(X), np.array(y)

    def set_train(self):
        """
        set the training data for prediction
        Args:
            df (DataFrame): dataframe
            interval (int, optional): interval in minutes. Defaults to 1.
            windows_size: window size
        """
        # create the dataset as list of timeseries, each timeseries corresponds to list of detection for one area
        dataset = []

        for col in self.df.columns:
            tmp = self.df[col].dropna().tolist()
            # skip timseries that have less then timestamps (equal to 1h of detection) since they are too small
            if len(tmp) >= 6:
                dataset.append(tmp)


        # length of the smaller timeseries
        self.window_size = 18

        data_train, data_test = train_test_split(dataset, test_size=0.1, shuffle=True, random_state=1)

        X_train, y_train = self.split_series(data_train, self.window_size)
        X_test, y_test = self.split_series(data_test, self.window_size)

        # remove duplicated timeseries
        X_train, filtered_index = np.unique(X_train, axis=0, return_index=True)
        y_train = y_train[filtered_index]

        X_test, filtered_index = np.unique(X_test, axis=0, return_index=True)
        y_test = y_test[filtered_index]

        # adjust shape for lstm model
        X_train = X_train[:, :, np.newaxis]

        # adjust shape for lstm model
        X_test = X_test[:, :, np.newaxis]
        return X_train, X_test, y_train, y_test 
    
    def split(self, X, Y, size = 0.1):
        X = X[:,:, np.newaxis]
        return train_test_split(X, Y, test_size=size)
    
    def build_model(self, layers, units, bidirectional=False, dropout=0.2):
        model = keras.Sequential()
        if bidirectional:
            #first layer
            model.add(Bidirectional(LSTM(units, return_sequences=True, input_shape=[None, 1])))

            # hidden layer
            for i in range(layers -1):
                model.add(Bidirectional(LSTM(units, return_sequences=True)))
                
            model.add(Bidirectional(LSTM(units)))
        else:
            #first layer
            model.add(LSTM(units, return_sequences=True, input_shape=[None, 1]))

            # hidden layer
            for i in range(layers -1):
                model.add(LSTM(units, return_sequences=True))
            model.add(LSTM(units))

        model.add(Dropout(dropout))

        # output layer
        model.add(Dense(1))

        model.compile(loss="mse", optimizer="adam")

        return model



    def fit(self, X_train, X_test, Y_train, Y_test):
        stop_early = EarlyStopping(monitor='val_loss', restore_best_weights=True, patience=5)
        cb = [stop_early]
        epochs = 100
        # take best parameters from csv file
        #row = kfold_cv_df.iloc[0]
        #units = row["units"]
        #layers = row["layers"]
        #bidirectional = row["bidirectional"]
        #dropout = row["dropout"]
        self.model = self.build_model(layers=2, units=50, bidirectional=False, dropout=0.1)

        history = self.model.fit(X_train, Y_train, epochs=epochs,
                    validation_split=0.2,
                    callbacks=cb)
        path="./prediction_model"
        self.model.save(path)
        with open(pm_vars_path, "w") as file:
            json.dump({
                "window_size": self.window_size
            }, file)


    def process_json(self, past_file, save_id=True):
        temp = pd.DataFrame(past_file)
        df = pd.DataFrame(columns=["id", "id_area", "id_building", "timestamp", "x", "y"])
        for i in range(len(temp.index)):
            pd_df = pd.DataFrame(temp["position_detections"].iloc[i])
            df = df.append(pd_df, ignore_index=True)

        df.set_index("id")

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp")

        # extract unique areas
        unique_areas = df["id_area"].unique()

        # group the df with timestamps of 10 minutes
        # and create a new dataframe
        # columns: id of the areas
        # value for each colum counter of devices in the range of 10 minutes
        minutes = '10T'

        new_df = pd.DataFrame()

        for elem in unique_areas:
            grouped_df = df['x'].where(df['id_area'] == int(elem)).groupby(
                pd.to_datetime(df["timestamp"]).dt.floor(minutes)).count()
            col_name = str(elem)
            temp_df = pd.DataFrame(data=grouped_df.to_list(), columns=[col_name])

            new_df = pd.concat([new_df, temp_df], axis=1)


        # new_df.drop(columns=['-1'], inplace=True)

        if save_id:
            # salva anche l'id dell'area
            dataset = {}
            for col in new_df.columns:
                tmp = new_df[col].dropna().tolist()
                dataset[col]=tmp
            return dataset
        else:
            return new_df

    def setup(self, filename):
        content = json.load(open(filename))
        new_df = self.process_json(content, save_id=False)

        self.df = new_df

        X_train, X_test, Y_train, Y_test = self.set_train()
        self.fit(X_train, X_test, Y_train, Y_test)
    
    def make_predictions(self, building=0, timeseries=None, future_steps=1):
        l = []

        for i in range(future_steps):
            res = self.model.predict(timeseries, verbose=0)
            
            # round to int the prediction array and set it to the correct shape
            res = np.rint(res)
            res = np.squeeze(res)
            
            l.append(int(res))
            
            timeseries_tmp=np.squeeze(timeseries, axis=0)
                        
            # delete first element of the timseries and append the prediction to this timeseries
            # in order to predict multiple steps dinamically
            timeseries = np.delete(timeseries, 0, axis=1)
            timeseries = np.append(timeseries, res)
            timeseries = timeseries[np.newaxis, :, np.newaxis]
        
        return l

    

    def predict(self, past_file, future_steps=5):
        dataset = self.process_json(past_file, save_id = True)
        prediction_dict={}
        for id, timeseries in dataset.items():
            #la timseries deve essere della stessa lunghezza che è stata utilizzata per trainare il modello, quindi prendiamo gli utilimi sliding_window_size step
            timeseries = np.array(timeseries)
            timeseries = timeseries[-self.window_size:]

            #adjust dimension in order to pass it to the model
            timeseries = timeseries[np.newaxis, :, np.newaxis]
            predictions = self.make_predictions(building = id, timeseries=timeseries, future_steps=future_steps)
            prediction_dict[str(id)] = predictions

        return prediction_dict
    
    def fit_predict(self):
        """predict and fit the model with the last observed data
        """
        
        
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
        path="./prediction_model"
        self.model = tf.keras.models.load_model(path)

