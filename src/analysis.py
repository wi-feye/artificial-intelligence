from positioning import *
from mapping import *
from utils import *

def enrich_points(xy_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Compute an enriched geodataframe of probe request. For each record (probe request) there is a new feature space
    that is the area where the point is within, and all the features of the relative space.
    See https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html to more info. 

    Args:
        xy_df (pd.DataFrame): dataframe with rssi signals and the position (x,y) for each probe request

    Returns:
        gpd.GeoDataFrame: geodataframe of probe request enriched
    """

    gdf_building = geo_building()
    gdf_points = geo_points(xy_df)
    gdf_points = gdf_points.sjoin(gdf_building)
    gdf_points.drop(['index_right'], axis=1, inplace=True)
    
    return gdf_points

def enrich_spaces(xy_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Compute an enriched geodataframe of the building. For each space (area or room) there are new features as
    #MAC, %MAC, area and density.

    Args:
        xy_df (pd.DataFrame): dataframe with rssi signals and the position (x,y) for each probe request

    Returns:
        gpd.GeoDataFrame: geodataframe of building enriched
    """

    gdf_points_enriched = enrich_points(xy_df)

    gdf_building = geo_building()
    gdf_building = gdf_building.set_index('space').join(gdf_points_enriched['space'].value_counts())
    gdf_building.fillna(0, inplace=True)
    gdf_building.rename(columns={"space": "count"}, inplace=True)
    gdf_building.reset_index(inplace=True)

    gdf_building['count_pct'] = gdf_building['count'] / gdf_building['count'].sum()
    gdf_building['area'] = gdf_building['geometry'].area
    gdf_building['density'] = gdf_building['count'] / gdf_building['area']

    return gdf_building


def apply_enrich_tt(xy_df: pd.DataFrame, enrichf, freq="2H", times=5, when:datetime=None) -> List[gpd.GeoDataFrame]:
    """_summary_

    Args:
        xy_df (pd.DataFrame): dataframe with rssi signals and the position (x,y) for each probe request
        enrichf (function (pd.DataFrame) -> gpd.GeoDataFrame): enrich_points or enrich_spaces
        freq (str, optional): delta time. Defaults to "2H".
        times (int, optional): number of ranges. Defaults to 5.
        when (datetime.datetime, optional): starting datetime. Defaults to None.

    Returns:
        List[gpd.GeoDataFrame]: list of geodataframe, one for each range of time
    """

    if when == None:
        when = xy_df['timestamp'].min()

    xy_df_list = generate_time_every(xy_df, freq, times, when)

    gdf_list = []
    for xy_df in xy_df_list:
        if not xy_df.empty:
            gdf_list.append(enrichf(xy_df))

    return gdf_list