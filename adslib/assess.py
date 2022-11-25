import osmnx as ox
from shapely.geometry import Point

def compute_cpa(data):
    data_means = np.mean(data, axis = 0)
    data_centered = data - data_means
    cov_mat = np.cov(centered_spectra , rowvar = False)
    eigen_values , eigen_vectors = np.linalg.eigh(cov_mat)
    
    sorted_idx = np.argsort(eigen_values)[::-1]
    sorted_eigenvalues = eigen_values[sorted_idx]
    sorted_eigenvectors = eigen_vectors[:,sorted_idx]
    
    return sorted_eigenvalues, sorted_eigenvectors, data_means

def invert_cpa(data, eigenvectors, means):
    return np.dot(eigenvectors, np.dot(eigenvectors.transpose(),(data - means).transpose())).transpose() + means

def get_features_around_coord(latitude, longitude, radius, tags, feature_set = []):
    if len(feature_set) == 0:
        return ox.geometries_from_point((latitude, longitude), tags, dist = radius)
    else:
        return ox.geometries_from_point((latitude, longitude), tags, dist = radius)[feature_set]

def extract_number_features(latitude, longitude, distance, feature_tag):
    features_in_radius = ox.geometries_from_point((latitude, longitude), feature_tag, dist = distance)
    len(features_in_radius)
    
extract_existance_feature = lambda latitude, longitude, distance, feature_tag : extract_number_features(latitude, longitude, distance, feature_tag) >= 1
 
def extract_distance_to_closest_feature_single(latitude, longitude, feature_tag, limit_distance = 5000):
    features_in_radius = ox.geometries_from_point((latitude, longitude), feature_tag, dist = limit_distance)
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
    box_height = building_data.latitude.max() - building_data.latitude.min() + 2*padding
    latitude = (building_data.latitude.max() + building_data.latitude.min())/2
    box_width = building_data.longitude.max() - building_data.longitude.min() + 2*padding
    longitude = (building_data.latitude.max() + building_data.latitude.min())/2
    
    osm_buildings = ox.geometries_from_bbox(latitude, longitude, box_height, box_width, {'building': True})
    osm_centroids = osm_buildings.geometry.centroid
    matches = building_data.apply(lambda x: osm_centroids.distance(Point(x.latitude, x.longitude)).argmin())
    return osm_buildings.iloc[matches][geometries_features]

def extract_distance_to_closest_feature_in_box(building_data, tags, padding = 0.06):
    box_height = building_data.latitude.max() - building_data.latitude.min() + 2*padding
    latitude = (building_data.latitude.max() + building_data.latitude.min())/2
    box_width = building_data.longitude.max() - building_data.longitude.min() + 2*padding
    longitude = (building_data.latitude.max() + building_data.latitude.min())/2
    
    osm_buildings = ox.geometries_from_bbox(latitude, longitude, box_height, box_width, tags)
    if len(osm_buildings) == 0:
        return None
    osm_centroids = osm_buildings.geometry.centroid
    return  building_data.apply(lambda x: osm_centroids.distance(Point(x.latitude, x.longitude)).min())

def extract_number_of_features_in_box(building_data, tags):
    box_height = building_data.latitude.max() - building_data.latitude.min() + 2*padding
    latitude = (building_data.latitude.max() + building_data.latitude.min())/2
    box_width = building_data.longitude.max() - building_data.longitude.min() + 2*padding
    longitude = (building_data.latitude.max() + building_data.latitude.min())/2
    
    osm_buildings = ox.geometries_from_bbox(latitude, longitude, box_height, box_width, tags)
    return len(osm_buildings)

extract_feature_existence_in_box = lambda building_data, tags: extract_number_of_features_in_box(building_data, tags) > 0
def match_single_building(latitude, longitude):
    radius = 100
    buildings_in_radius = get_features_around_coord(latitude, longitude, radius, {'building': True})
    distances = buildings_in_radius.geometry.centroid.distance(Point(latitude, longitude))
    return buildings_in_radius[distances.argmin()]