import json
import pandas as pd
from pandas import DataFrame
import numpy as np

class Positioning:
    def __init__(self, measurements: str, devices: str, areas: str):
        """
        The class Positioning provide a method to retrieve the 2-Dimensional position from measurements taken from 
        zenith devices
        :param measurements: string that represents a list of measurement, should be formatted in json, 
        throws exception otherwise.
        :param devices: string that represents a list of devices, should be formatted in json, throws exception 
        otherwise     
        :param areas: string that represents a list of areas to user for labelling the points
        should be formatted in json, throws exception otherwise 
        """
        
        # ============== VALIDATION OF INPUT DATA ==============
        if (not isinstance(measurements, str)) or (not isinstance(devices, str)) or (not isinstance(areas, str)):
            raise Exception("Input data are not string!")

        if (not self.__is_json(measurements)) or (not self.__is_json(devices)) or (not self.__is_json(areas)):
            raise Exception("Input data are not json!")
        
        # add here furter validiy
        # ============== VALIDATION OF INPUT DATA ==============
        
        # First of all we transform the dictionary (taken from function "loads") and we transform it into dataframe,
        # but we need to manage the array inside.
        self.__measurements: DataFrame = pd.DataFrame(json.loads(measurements))
        # Same things 
        self.__sniffers: DataFrame = pd.DataFrame(json.loads(devices))
        
        # Oss. We take the order of the sniffer from the order of device json
        
        # (This function simply assign a sort of "priority" 0,1,2... )
        self.__ids_to_order: dict = {values["id"]: order for order, values in enumerate(json.loads(devices))}
        # We retrieve a sniffer list (with the same order)
        self.__sniffers_list: list = list(self.__sniffers[["x", "y"]].itertuples(index=False, name=None))
        
        # just parameters which we can modify if occurs
        self.__rss0: int = -54
        self.__n_env: float = 3.6
    
    def perform_xy(self) -> DataFrame:
        """
        This function take the dataframe calculated in the initial phase and return another dataframe 
        where there are for each point the sequent infomations:
         id (of the point) ; list of sniffer with their name ; x (x position) y (y position)
         es : 
         | Id | Sniffer 1 |  Sniffer 1 |  Sniffer 1 | x | y
         | 51 | -84       |  -63       |  -21       | 8.511 | 17.55
        :return: 
        """
        result_rows = []
        
        # foreach measurement
        for _, row in self.__measurements[["id", "devices"]].iterrows():
            
            # we take the index of row (es 1001) and a list of dictionary which represent the sniffers
            index, dicts_list = row[0], row[1]
            
            # We create a list contain the rssi of the sniffer, the order is not always the same, and this is a problem
            # in order to overcome this we need to maintain attach which is the sniffer linked to rssi values
            rssi_list = [(sub_dict["rssi"], self.__ids_to_order[sub_dict["id"]]) for sub_dict in dicts_list]

            # why? because now we order the rssi's based on priority define in the init
            right_order_rssi = sorted(rssi_list, key=lambda t: t[1])
            # We remove the "priority" to obtain only a list of rssi
            right_order_rssi = [couple[0] for couple in right_order_rssi]
            
            # we use the position function to get the distance
            result_rows.append([index] + right_order_rssi + list(self.__position(right_order_rssi)))
        
        # finally we transform the list of list into dataframe
        cols = ["id"] + self.__sniffers["name"].to_list() + ["x", "y"]
        final = pd.DataFrame(result_rows, columns=cols).set_index("id")
        return final

    @staticmethod
    def __is_json(myjson: str) -> bool:
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True

    def __position(self, rss_list: list) -> tuple:
        # par = Parameter()
        if len(rss_list) >= 3:
            P = np.array(self.__sniffers_list)
            temp_A = P[-1] - P
            temp_A = temp_A[0:-1]
            A = 2 * temp_A

            # from rssi to distance in meters
            def rss_to_dist(rss: int, nu_env: float) -> float:
                return np.power(10, (self.__rss0 - rss) / (10 * nu_env))

            d = np.empty((0, 1))
            for rss in rss_list:
                d = np.append(d, [[rss_to_dist(rss, self.__n_env)]], axis=0)

            d_2 = np.power(d, 2)
            temp_d = d_2 - d_2[-1]
            temp_d = temp_d[0:-1]

            P_2 = np.power(P, 2)
            temp_b1 = P_2[-1] - P_2
            temp_b1 = temp_b1[0:-1]

            b = np.einsum('ij->i', temp_b1).reshape(temp_d.shape) + temp_d

            X = np.dot(np.linalg.pinv(A), b)

            x, y = X[0][0], X[1][0]
        else:
            sniffer_index_max = np.argmax(rss_list)
            x = self.__sniffers_list[sniffer_index_max][0]
            y = self.__sniffers_list[sniffer_index_max][1]

        return x, y
    
    
# source1 , source2 and 3 are json from backend requeste!!!!
p = Positioning(measurements, devices, areas)
p.perform_xy()
