import json
from typing import Tuple
import pandas as pd
from pandas import DataFrame
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import geopandas as gpd

class Positioning:
    def __init__(self, building: json):
        """_summary_

        Args:
            building (json): _description_
        """

        self.__measurements = building['raws']

        self.__areas: GeoDataFrame = gpd.GeoDataFrame(building['areas'])
        self.__areas['geometry'] = self.__areas['location'].apply(lambda x: Polygon(x))
        self.__areas.drop("location", axis=1, inplace=True)
        self.__areas = self.__areas.rename(columns={"id": "id_area", "name": "name_area"}) # Rename columns
        
        self.__sniffers_list: list = {device['id']: [device['x'], device['y']] for device in building['sniffers']}

        # -------------------- parameters --------------------
        self.__rss0: int = -54
        self.__n_env: float = 3.6
        # -------------------- parameters --------------------

    def perform_xy(self) -> pd.DataFrame:
        """
        This function take the dataframe calculated in the initial phase and return another dataframe
        where there are for each point the sequent information:
         id (of the point) ; list of sniffer with their name ; x (x position) y (y position)
         es :
         | Id   | timestamp             | x     | y
         | 51   | 2022-11-09 17:16:00   | 8.511 | 17.55
        :return:
        """
        result_rows = [] 

        for measurement in self.__measurements:

            index = measurement['id']
            timestamp = measurement['timestamp']
            rssi_device = measurement['rssi_device']

            result_rows.append([index, timestamp] + list(self.__position(rssi_device)))

        cols = ["id", "timestamp"] + ["x", "y"]

        result: DataFrame = pd.DataFrame(result_rows, columns=cols).set_index("id")

        return result

    def __position(self, rss_list: list) -> Tuple[float, float]:
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
            sniffer_index_max = np.argmax(rss_list)
            x = self.__sniffers_list[sniffer_index_max][0]
            y = self.__sniffers_list[sniffer_index_max][1]

        return x, y

    def assign_area(self, df: pd.DataFrame) -> pd.DataFrame:
        """        
        | Id | x       | y     | id_area
        | 51 | 8.511   | 17.55 | 105

        Args:
            df (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """
        geo_points: GeoDataFrame = gpd.GeoDataFrame(df[["x", "y"]])
        geo_points['geometry'] = gpd.points_from_xy(geo_points['x'], geo_points['y'])
        
        # Compute the area of each points
        geo_points = geo_points.sjoin(self.__areas, how="left")
        geo_points.drop(['index_right'], axis=1, inplace=True)
        geo_points.fillna("-1", inplace=True) # -1 if point is outside the building
        
        geo_points["id_area"] = geo_points["id_area"].astype(int)
        
        return geo_points[["x", "y", "id_area"]]
