import osmnx as ox
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoints

''' Selects all POIs, given by tags, within a certain distance around a point.
    :param latitude: The latitude of the center point
    :param longitude: The longitude of the center point
    :param distance: The maximum distance away from the point to be considered
    :param tags: A dictionary of OSM-style tags to be considered
    :param feature_set: A list of features to be extracted from the resulting query
    :return: A GeoDataFrame of POIs
'''
def get_features_around_coord(latitude, longitude, distance, tags, feature_set = []):
    if len(feature_set) == 0:
        return ox.geometries_from_point((latitude, longitude), tags, dist = distance)
    else:
        return ox.geometries_from_point((latitude, longitude), tags, dist = distance)[feature_set]


''' # Returns the number of POIs up to a certain distance from point
    :param latitude: The latitude of the center point
    :param longitude: The longitude of the center point
    :param distance: The maximum distance away from the point to be considered
    :param tags: A dictionary of OSM-style tags to be considered
    :return: The number of POIs
'''
def extract_number_features(latitude, longitude, distance, tags):
    features_in_radius = ox.geometries_from_point((latitude, longitude), tags, dist = distance)
    return len(features_in_radius)
 
''' # The existence of a feature is defined by checking whether the number of features is at least 1
    :param latitude: The latitude of the center point
    :param longitude: The longitude of the center point
    :param distance: The maximum distance away from the point to be considered
    :param tags: A dictionary of OSM-style tags to be considered
    :return: A boolean showing whether if any POI exists
'''   
extract_existance_feature = lambda latitude, longitude, distance, tags : extract_number_features(latitude, longitude, distance, tags) >= 1
 
''' Takes the distance to the closest POI from point
    :param latitude: The latitude of the center point
    :param longitude: The longitude of the center point
    :param feature_tag: The tag(s) to be considered for the POIs
    :param limit_distance: The maximum distance to be considered valid
    :return: The distance to the closest feature or None
'''   
def extract_distance_to_closest_feature_single(latitude, longitude, feature_tag, limit_distance = 5000):
    features_in_radius = ox.geometries_from_point((latitude, longitude), feature_tag, dist = limit_distance)
    if len(features_in_radius) == 0:
        return None
    point = gpd.GeoSeries(Point(longitude, latitude)).set_crs(4326).to_crs(27700)
    distances = features_in_radius.to_crs(27700).geometry.centroid.apply(lambda x: point.distance(x))
    return distances[0].min()

''' Returns the matching building for a given point
    :param latitude: The latitude of the center point
    :param longitude: The longitude of the center point
    :return: The closest building or None if no match is found
'''  
def match_single_building(latitude, longitude):
    radius = 300
    buildings_in_radius = get_features_around_coord(latitude, longitude, radius, {'building': True})
    if len(buildings_in_radius) == 0:
        return None
    point = gpd.GeoSeries(Point(longitude, latitude)).set_crs(4326).to_crs(27700)
    distances = buildings_in_radius.to_crs(27700).geometry.centroid.apply(lambda x: point.distance(x))
    buildings_in_radius['is_valid_match'] = True
    return buildings_in_radius.iloc[distances[0].argmin()]


''' Private method to compute the mean radius of a polygon
    :param poly: A Polygon
    :return: The radius, as the mean of the distance from the centroid to exterior points
'''  
def __polygon_radius__(poly):
    centroid = poly.centroid
    exterior_points = gpd.GeoSeries([Point(i) for i in poly.exterior.coords])
    return exterior_points.apply(lambda x: centroid.distance(x)).mean()

''' Method to get the size, importance and centroid of a city/town/village
    :param city: The name of the place
    :param country: The country of the place
    :param county: The county, to which the place belongs
    :return: The radius, importance metric and the centroid of the place
'''  
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
    # Geometries are encoded as either Polygons or a set of Polygons(MultiPolygon)
    # For the latter, we define the radius as the Euclidean magnitude of the list of polygon radiuses
    if place.geometry.geom_type == 'MultiPolygon':
        multi_radius = np.array([__polygon_radius__(poly) for poly in place_data.geometry.to_crs(27700)[0]])
        radius = ((multi_radius**2).sum())**(1/2)
    elif place.geometry.geom_type == 'Polygon':
        radius = __polygon_radius__(place_data.geometry.to_crs(27700)[0])
    else:
        return None    
    return {'place_center': centroid, 'importance': place.importance, 'radius': radius}

''' Loads all POIs with the given task within the boundary, determined by the set of buildings given
    :param building_data: A DataFrame, containing the buildings' features and coordinates
    :param tags: A dictionary of OSM-style tags to be considered
    :param padding: How much to extend the box by in each direction
    :return: A GeoDataFrame of POIs
'''
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

''' Loads all POIs with the given task within the boundary, determined by the set of buildings given
    :param building_data: A DataFrame, containing the buildings' features and coordinates
    :param tags: A dictionary of OSM-style tags to be considered
    :param padding: How much to extend the box by in each direction
    :return: A GeoDataFrame of POIs
'''
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
    
    # If not features are specified, return all
    if len(geometries_features) == 0:
        return matching_buildings
    
    # Otherwise select specific ones
    return matching_buildings[geometries_features]

''' Calculates the closest distance for each row to a set of POIs
    :param building_data: A DataFrame, containing the buildings' features and coordinates
    :param tags: A dictionary of OSM-style tags to be considered
    :param padding: How much to extend the box by in each direction
    :return: A series with the distance to the closest feature for each building
'''
def extract_distance_to_closest_feature_in_box(building_data, tags, padding = 0.02):
    features = get_geometries_in_region(building_data, tags, padding = padding)
    if len(features) == 0:
        return None
    centroids = features.to_crs(27700).geometry.centroid
    points = gpd.GeoSeries(building_data.apply(lambda x: Point(x.longitude, x.latitude), axis = 1)).set_crs(4326).to_crs(27700)
    return points.apply(lambda x: centroids.distance(x).min())

''' Calculates the number of features in a given box, determined by the set of buildings
    :param building_data: A DataFrame, containing the buildings' features and coordinates
    :param tags: A dictionary of OSM-style tags to be considered
    :param padding: How much to extend the box by in each direction
    :return: The number of features in the box
'''
def extract_number_of_features_in_box(building_data, tags, padding = 0.02):
    features = get_geometries_in_region(building_data, tags, padding = padding)
    return len(features)

''' For each row determines whether there exists a POI within a certain distance
    :param building_data: A DataFrame, containing the buildings' features and coordinates
    :param tags: A dictionary of OSM-style tags to be considered
    :param padding: How much to extend the box by in each direction
    :return: The number of features in the box
'''
def extract_feature_existence_in_box (building_data, tags, padding = 0.02, distance_limit = 500): 
    features = get_geometries_in_region(building_data, tags, padding = padding)
    if len(features) == 0:
        return False
    centroids = features.to_crs(27700).geometry.centroid
    points = gpd.GeoSeries(building_data.apply(lambda x: Point(x.longitude, x.latitude), axis = 1)).set_crs(4326).to_crs(27700)
    return points.apply(lambda x: centroids.distance(x).min()) < distance_limit
