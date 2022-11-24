import osmnx as ox
from shapely.geometry import Point


def get_features_around_coord(latitude, longitude, box_height, box_width, tags):
    north = latitude + box_height/2
    south = latitude - box_height/2
    east = longitude + box_width/2
    west = longitude - box_width/2
    return ox.geometries_from_bbox(north, south, east, west, tags)

print(get_features_around_coord(52.20028400, 0.14657900, 0.1, {'building:use':'residential'}))

def extract_number_features(latitude, longitude, distance, feature_tag):
    features_in_radius = ox.geometries_from_point(latitude, longitude, feature_tag, dist = distance)
    len(features_in_radius)
    
extract_existance_feature = lambda latitude, longitude, distance, feature_tag : extract_number_features(latitude, longitude, distance, feature_tag) >= 1
 
def extract_distance_to_closest_feature(latitude, longitude, feature_tag, limit_distance = 5000):
    features_in_radius = ox.geometries_from_point(latitude, longitude, feature_tag, dist = limit_distance)
    if len(features_in_radius) == 0:
        return None
    distances = features_in_radius.geometry.centroid.distance(Point(latitude, longitude))
    return min(distances)

def extract_place_features(city, country, county = ""):
    place_name = city
    if len(county) == 0:
        place_name += ', %s'%county
    place_name += ', %s'%country
    place_data = ox.geocode_to_gdf(place_name)[0]
    return {'place_center': place_data.geometry.centroid, 'importance': place_data.importance}

def extract_osm_building_features(building_data, geometries_features):
    box_height = building_data.latitude.max() - building_data.latitude.min()
    latitude = (building_data.latitude.max() + building_data.latitude.min())/2
    box_width = building_data.longitude.max() - building_data.longitude.min()
    longitude = (building_data.latitude.max() + building_data.latitude.min())/2
    
    osm_buildings = get_features_around_coord(latitude, longitude, box_height, box_width, {'building': True})
    osm_centroids = osm_buildings.geometry.centroid
    matches = building_data.apply(lambda x: osm_centroids.distance(Point(x.latitude, x.longitude)).argmin())
    return osm_buildings.iloc[matches][geometries_features]

def match_single_building(latitude, longitude):
    radius = 0.001 # Approximately 110m in latitude, longitude measure depends on latitude
    buildings_in_radius = get_features_around_coord(latitude, longitude, 2*radius, 2*radius, {'building': True})
    distances = buildings_in_radius.geometry.centroid.distance(Point(latitude, longitude))
    return buildings_in_radius[distances.argmin()]