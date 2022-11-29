import osmnx as ox
from shapely.geometry import Point, MultiPoint
import numpy as np
import pandas as pd
import geopandas as gpd
def compute_pca(data):
    data_means = np.mean(data, axis = 0)
    data_std = np.std(data_means, axis = 0)
    data_norm = (data - data_means)/data_std
    cov_mat = np.cov(data_norm , rowvar = False)
    eigen_values , eigen_vectors = np.linalg.eigh(cov_mat)
    
    sorted_idx = np.argsort(eigen_values)[::-1]
    sorted_eigenvalues = eigen_values[sorted_idx]
    sorted_eigenvectors = eigen_vectors[:,sorted_idx]
    
    return sorted_eigenvalues, sorted_eigenvectors, data_means, data_std

def invert_pca(data, eigenvectors, means):
    return np.dot(eigenvectors.transpose(), np.dot(eigenvectors,(data - means).transpose())).transpose() + means

def get_features_around_coord(latitude, longitude, radius, tags, feature_set = []):
    if len(feature_set) == 0:
        return ox.geometries_from_point((latitude, longitude), tags, dist = radius)
    else:
        return ox.geometries_from_point((latitude, longitude), tags, dist = radius)[feature_set]

def extract_number_features(latitude, longitude, distance, feature_tag):
    features_in_radius = ox.geometries_from_point((latitude, longitude), feature_tag, dist = distance)
    return len(features_in_radius)
    
extract_existance_feature = lambda latitude, longitude, distance, feature_tag : extract_number_features(latitude, longitude, distance, feature_tag) >= 1
 
def extract_distance_to_closest_feature_single(latitude, longitude, feature_tag, limit_distance = 5000):
    features_in_radius = ox.geometries_from_point((latitude, longitude), feature_tag, dist = limit_distance)
    if len(features_in_radius) == 0:
        return None
    point = gpd.GeoSeries(Point(longitude, latitude)).set_crs(4326).to_crs(27700)
    distances = features_in_radius.to_crs(27700).geometry.centroid.apply(lambda x: point.distance(x))
    return distances[0].min()

def match_single_building(latitude, longitude):
    radius = 500
    buildings_in_radius = get_features_around_coord(latitude, longitude, radius, {'building': True})
    point = gpd.GeoSeries(Point(longitude, latitude)).set_crs(4326).to_crs(27700)
    distances = buildings_in_radius.to_crs(27700).geometry.centroid.apply(lambda x: point.distance(x))
    return buildings_in_radius.iloc[distances[0].argmin()]

def __polygon_radius__(poly):
    centroid = poly.centroid
    exterior_points = gpd.GeoSeries([Point(i) for i in poly.exterior.coords])
    return exterior_points.apply(lambda x: centroid.distance(x)).mean()

def extract_place_features(city, country, county = ""):
    place_name = city
    if len(county) == 0:
        place_name += ', %s'%county
    place_name += ', %s'%country
    try:
        place_data = ox.geocode_to_gdf(place_name)
    except ValueError:
        return None
    if len(place_data) < 1:
        return None
    place = place_data.iloc[0]
    centroid = place_data.geometry.to_crs(27700)[0].centroid
    if place.geometry.geom_type == 'MultiPolygon':
        multi_radius = np.array([__polygon_radius__(poly) for poly in place_data.geometry.to_crs(27700)[0]])
        radius = ((multi_radius**2).sum())**(1/2)
    elif place.geometry.geom_type == 'Polygon':
        radius = __polygon_radius__(place_data.geometry.to_crs(27700)[0])
    else:
        return None    
    return {'place_center': centroid, 'importance': place.importance, 'radius': radius}

def get_geometries_in_region(building_data, tags, padding = 0.02):
    box_height = building_data.latitude.max() - building_data.latitude.min() + 2*padding
    latitude = (building_data.latitude.max() + building_data.latitude.min())/2
    box_width = building_data.longitude.max() - building_data.longitude.min() + 2*padding
    longitude = (building_data.longitude.max() + building_data.longitude.min())/2
    
    north = latitude + box_height/2
    south = latitude - box_height/2
    east = longitude + box_width/2
    west = longitude - box_width/2
    
    return ox.geometries_from_bbox(north, south, east, west, tags)

def extract_osm_building_features(building_data, geometries_features = [], padding = 0.02):
    buildings = get_geometries_in_region(building_data, {'building': True}, padding = padding)
    centroids = buildings.to_crs(27700).geometry.centroid
    if len(buildings) == 0:
        return None
    points = gpd.GeoSeries(building_data.apply(lambda x: Point(x.longitude, x.latitude), axis = 1)).set_crs(4326).to_crs(27700)
    matches = points.apply(lambda x: centroids.distance(x).argmin())
    matching_buildings = buildings.iloc[matches]
    matching_buildings.index = building_data.index
    matching_buildings['is_valid_match'] = points.apply(lambda x: centroids.distance(x).min()) < 150
    if len(geometries_features) == 0:
        return matching_buildings
    return matching_buildings[geometries_features]

def extract_distance_to_closest_feature_in_box(building_data, tags, padding = 0.02):
    features = get_geometries_in_region(building_data, tags, padding = padding)
    if len(features) == 0:
        return None
    centroids = features.to_crs(27700).geometry.centroid
    points = gpd.GeoSeries(building_data.apply(lambda x: Point(x.longitude, x.latitude), axis = 1)).set_crs(4326).to_crs(27700)
    return points.apply(lambda x: centroids.distance(x).min())

def extract_number_of_features_in_box(building_data, tags, padding = 0.02):
    features = get_geometries_in_region(building_data, tags, padding = padding)
    return len(features)

def extract_feature_existence_in_box (building_data, tags, padding = 0.02, distance_limit = 500): 
    features = get_geometries_in_region(building_data, tags, padding = padding)
    if len(features) == 0:
        return False
    centroids = features.to_crs(27700).geometry.centroid
    points = gpd.GeoSeries(building_data.apply(lambda x: Point(x.longitude, x.latitude), axis = 1)).set_crs(4326).to_crs(27700)
    return points.apply(lambda x: centroids.distance(x).min()) < distance_limit

def do_one_hot_encoding(df, feature):
    for feature_type in df[feature].unique():
        encoding_name = 'is_' + str(feature) + '_' + str(feature_type)
        df[encoding_name] = np.where(df[feature] == feature_type, 1, 0)
    return df

def remove_outliers(df, feature):
    quantiles = np.quantile(df[feature], [0.25, 0.75])
    iqr = quantiles[1] - quantiles[0]
    lower_bound = quantiles[0] - 1.5*iqr
    upper_bound = quantiles[1] + 1.5*iqr
    return df[(df[feature] <= upper_bound) & (df[feature] >= lower_bound)]