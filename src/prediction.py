from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity


def all_is_likelihood(xy_df: pd.DataFrame, kde: KernelDensity = None, threshold: float = float('-inf')) -> Tuple[pd.DataFrame, KernelDensity]:
    """Compute likelihood for each position (x,y)

    Args:
        xy_df (pd.DataFrame): _description_
        kde (KernelDensity, optional): _description_. Defaults to None.
        threshold (float, optional): _description_. Defaults to float('-inf').

    Returns:
        Tuple[pd.DataFrame, KernelDensity]: _description_
    """
    X = xy_df[['x','y']].to_numpy()
    if(kde == None):
        kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(X)
    
    xy_df['likelihood'] = kde.score_samples(X).tolist()
    xy_df = xy_df[xy_df['likelihood'] > threshold]
    
    return xy_df, kde
    

def likelihood(points: np.ndarray, kde: KernelDensity) -> np.ndarray:
    """Compute likelihood of points

    Args:
        points (np.ndarray): _description_
        kde (KernelDensity): _description_

    Returns:
        np.ndarray: _description_
    """
    return kde.score_samples(points)


def points_of_interest(xy_df: pd.DataFrame, kde: KernelDensity, threshold: float = -2) -> np.ndarray:
    """Given a dataframe of points retrieve the more interest points

    Args:
        xy_df (pd.DataFrame): _description_
        kde (KernelDensity): _description_
        threshold (float, optional): _description_. Defaults to -2.

    Returns:
        np.ndarray: _description_
    """
    points = xy_df[['x','y']].to_numpy()
    score = likelihood(points, kde)
    return points[score > threshold]


def sample(kde: KernelDensity, n_samples: int = 1) -> np.ndarray:
    """Generate samples given a distribution pre-fitted

    Args:
        kde (KernelDensity): _description_
        n_samples (int, optional): _description_. Defaults to 1.

    Returns:
        np.ndarray: _description_
    """
    return kde.sample(n_samples)


def sampling(xy_df: pd.DataFrame, n_samples: int = 1) -> np.ndarray:
    """From a dataframe of points, estimate the distribution and generate samples

    Args:
        xy_df (pd.DataFrame): _description_
        n_samples (int, optional): _description_. Defaults to 1.

    Returns:
        np.ndarray: _description_
    """
    X = xy_df[['x','y']].to_numpy()
    kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(X)
    return sample(kde, n_samples)