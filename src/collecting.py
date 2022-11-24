import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

class Collecting:
    def __init__(self, measurements: dict, devices: dict, areas: dict):
        """
        The class Positioning provides a methods to retrieve the 2-Dimensional position from measurements taken from
        zenith devices, further, give a different areas return the corresponding area for each point.
        :param measurements: string that represents a list of measurement, should be formatted in json,
        throws exception otherwise.
        :param devices: string that represents a list of devices, should be formatted in json, throws exception
        otherwise
        :param areas: string that represents a list of areas to user for labelling the points
        should be formatted in json, throws exception otherwise
        """

        # ============== VALIDATION OF INPUT DATA ==============
        # if (not isinstance(measurements, str)) or (not isinstance(devices, str)) or (not isinstance(areas, str)):
        #     raise Exception("Input data are not string!")

        # if (not self.__is_json(measurements)) or (not self.__is_json(devices)) or (not self.__is_json(areas)):
        #     raise Exception("Input data are not json!")

        # add here further valid procedures
        # ============== VALIDATION OF INPUT DATA ==============

        # -------------------- measurements --------------------
        # First of all we process the dictionary (taken from function "loads") and we transform it into dataframe,
        # but we need to manage the array inside (next steps).
        self.__measurements: pd.DataFrame = pd.DataFrame(measurements)
        self.__measurements.timestamp = pd.to_datetime(self.__measurements.timestamp, format="%Y-%m-%d %H:%M:%S").apply(
            lambda x: x.replace(second=0, microsecond=0))
        # -------------------- measurements --------------------

        # -------------------- devices --------------------
        self.__sniffers: pd.DataFrame = pd.DataFrame(devices)
        # -------------------- devices --------------------

        # -------------------- areas --------------------
        self.__areas: gpd.GeoDataFrame = gpd.GeoDataFrame(areas)
        # we create a polygons, oss the column must be called "geometry"
        self.__areas['geometry'] = self.__areas['location'].apply(lambda x: Polygon(x))
        self.__areas.drop("location", axis=1, inplace=True)
        # we rename the columns just for avoid misunderstanding
        self.__areas = self.__areas.rename(columns={"id": "id_area", "name": "name_area"})
        # -------------------- areas --------------------

        # Oss. We take the order of the sniffer from the order of device json
        # (This function simply assign a sort of "priority" 0,1,2... )
        self.__ids_to_order: dict = {values["id"]: order for order, values in enumerate(devices)}
        # We retrieve a sniffer list (with the same order)
        self.__sniffers_list: list = list(self.__sniffers[["x", "y"]].itertuples(index=False, name=None))

        # -------------------- parameters --------------------
        self.__rss0: int = -54
        self.__n_env: float = 3.6
        # -------------------- parameters --------------------
        
    def collect(self) -> pd.DataFrame:
        """
        This function take the dataframe calculated in the initial phase and return another dataframe
        where there are for each point the sequent information:
            id (of the point) ; list of sniffer with their name ; x (x position) y (y position)
            es :
            | Id   | timestamp             | x     | y
            | 51   | 2022-11-09 17:16:00   | 8.511 | 17.55
        :return:
        """
        result_rows = []  # list of lists used to create a final dataframe

        for _, row in self.__measurements[["id", "rssi_device", "timestamp"]].iterrows():
            # we take the index of row (es 1001) and a list of dictionary which represent the sniffers
            index, dicts_list, timestamp = row[0], row[1], row[2]

            # We create a list contain the rssi of the sniffer, the order is not always the same, and this is a problem
            # in order to overcome this we need to maintain attach which is the sniffer linked to rssi values
            rssi_list = [(sub_dict["rssi"], self.__ids_to_order[int(sub_dict["id"])]) for sub_dict in dicts_list]

            # why? because now we order the rssi's based on priority define in the init
            right_order_rssi = sorted(rssi_list, key=lambda t: t[1])
            # We remove the "priority" to obtain only a list of rssi
            right_order_rssi = [couple[0] for couple in right_order_rssi]

            result_rows.append([index, timestamp] + list(right_order_rssi))

        cols = ["id", "timestamp"] + ["x", "y"]  # self.__sniffers["name"].to_list()

        result: pd.DataFrame = pd.DataFrame(result_rows, columns=cols).set_index("id")

        return result

    def assign_area(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This function takes the dataframe which was calculated the 2D position and return
        another dataframe where there are the sequent information:
        es:
         | Id | x       | y     | id_area
         | 51 | 8.511   | 17.55 | 105
         The id_area refers to a unique id of the area taken from "area json file"
        :param df:
        :return:
        """
        geo_points: gpd.GeoDataFrame = gpd.GeoDataFrame(df[["x", "y"]])
        geo_points['geometry'] = gpd.points_from_xy(geo_points['x'], geo_points['y'])
        # intersect the geometry of point with the geometry of areas in order to indicate if a point 
        # is inside a one specific area.
        geo_points = geo_points.sjoin(self.__areas, how="left")
        geo_points.drop(['index_right'], axis=1, inplace=True)
        # oss if the point does not belong to any area, it returns a -1
        geo_points.fillna("-1", inplace=True)
        geo_points["id_area"] = geo_points["id_area"].astype(int)
        
        return geo_points[["x", "y", "id_area"]]

    @staticmethod
    def return_json(df: pd.DataFrame) -> str:
        df["id"] = df.index
        return df.to_dict(orient="records")