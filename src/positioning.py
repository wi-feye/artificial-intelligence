import json
from typing import Tuple
import pandas as pd
from pandas import DataFrame
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import geopandas as gpd

class Positioning:
    def __init__(self, building_raw: json, rss0: int = -54, n_env: float = 3.6):
        """_summary_

        Args:
            building_raw (dict): _description_
        """

        self.__measurements = building_raw['raws']

        self.__areas: GeoDataFrame = gpd.GeoDataFrame(building_raw['areas'])
        self.__areas['geometry'] = self.__areas['location'].apply(lambda x: Polygon(x))
        self.__areas.drop("location", axis=1, inplace=True)
        self.__areas = self.__areas.rename(columns={"id": "id_area", "name": "name_area"}) # Rename columns
        
        self.__sniffers_list: dict = {device['id']: [device['x'], device['y']] for device in building_raw['sniffers']}

        # -------------------- parameters --------------------
        self.__rss0: int = rss0
        self.__n_env: float = n_env
        # -------------------- parameters --------------------
        
        
    def __position(self, rss_list: list) -> Tuple[float, float]:
        """From rssi list to position

        Args:
            rss_list (list): list of rssi

        Returns:
            Tuple[float, float]: x, y
        """
        if len(rss_list) >= 3:
            xy_matrix = [self.__sniffers_list[rss['id']] for rss in rss_list]
            P = np.array(xy_matrix)
            temp_A = P[-1] - P
            temp_A = temp_A[0:-1]
            A = 2 * temp_A

            # from rssi to distance in meters
            def rss_to_dist(rss: int, nu_env: float) -> float:
                return np.power(10, (self.__rss0 - rss) / (10 * nu_env))

            d = np.empty((0, 1))
            for rss in rss_list:
                d = np.append(d, [[rss_to_dist(rss['rssi'], self.__n_env)]], axis=0)

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
            max = float("-inf")
            for rss in rss_list:
                if rss['rssi'] > max:
                    max = rss['rssi']
                    sniffer_index_max = rss['id']
            # sniffer_index_max = np.argmax(rss_list)
            x = self.__sniffers_list[sniffer_index_max][0]
            y = self.__sniffers_list[sniffer_index_max][1]

        return x, y
    

    def perform_xy(self) -> pd.DataFrame:
        """
        | Id   | timestamp             | x     | y
        | 51   | 2022-11-09 17:16:00   | 8.511 | 17.55

        Returns:
            pd.DataFrame: _description_
        """
        result_rows = [] 

        for measurement in self.__measurements:

            index = measurement['id']
            timestamp = measurement['timestamp']
            rssi_device = measurement['rssi_device']

            result_rows.append([index, timestamp] + list(self.__position(rssi_device)))

        cols = ["id", "timestamp"] + ["x", "y"]

        result: DataFrame = pd.DataFrame(result_rows, columns=cols).set_index("id")
        result[['x','y']] = result[['x','y']].round(2)

        return result


    def assign_area(self, df: pd.DataFrame) -> pd.DataFrame:
        """        
        | Id | x       | y     | id_area
        | 51 | 8.511   | 17.55 | 105

        Args:
            df (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """
        geo_points: GeoDataFrame = gpd.GeoDataFrame(df[["x", "y", "timestamp"]])
        geo_points['geometry'] = gpd.points_from_xy(geo_points['x'], geo_points['y'])
        
        # Compute the area of each points
        geo_points = geo_points.sjoin(self.__areas, how="left")
        geo_points.drop(['index_right'], axis=1, inplace=True)
        geo_points.dropna(inplace=True) # drop point if point is outside the building
        
        geo_points["id_area"] = geo_points["id_area"].astype(int)
        
        return geo_points[["x", "y", "id_area","timestamp"]]
