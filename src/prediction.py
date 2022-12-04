from typing import Tuple
import pandas as pd
from sklearn.neighbors import KernelDensity


class Prediction:
    def __init__(self, building_position: dict) -> None:
        self.__xy_df: pd.DataFrame = pd.DataFrame(building_position['position_detections'])


    def poi(self, bandwith: float = 0.2, top: int = 5, buffer: float = 10) -> pd.DataFrame:
        """Compute points of interest with respective likelihood (log-likelihood)

        Args:
            bandwith (float, optional): _description_. Defaults to 0.2.
            top (int, optional): _description_. Defaults to 5.
            buffer (float, optional): _description_. Defaults to 10.

        Returns:
            pd.DataFrame: _description_
        """
        df = self.__xy_df
        df = df.loc[df['id_area'] != -1]
        df = df.drop(columns = 'timestamp')
        X = df[['x','y']].to_numpy()
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwith).fit(X)
        df['likelihood'] = kde.score_samples(X).tolist()

        df_buffer = df.copy()
        df_buffer[['x','y']] = df_buffer[['x','y']].apply(lambda x: round(x / buffer))
        df_buffer = df_buffer.loc[df_buffer.groupby(by=['x','y'])['likelihood'].idxmax()]
        poi_df = df[df.index.isin(df_buffer.index)]
            
        if(top < poi_df.shape[0]):
            poi_df = poi_df.nlargest(top,'likelihood')
        else:
            poi_df = poi_df.sort_values('likelihood', ascending=False)
        
        return poi_df