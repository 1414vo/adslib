import numpy as np
import pandas as pd

''' Computes the eigenvector decomposition for a given dataset.
    :param data: Numpy array, containing our data, with columns as the dimensions.
    :return: The eigen-representation, alongside the mean and standard deviation computed per column
'''
def compute_pca(data):
    # Normalize the data before computing the covariance matrix
    # Normalization
    data_means = np.mean(data, axis = 0)
    data_std = np.std(data, axis = 0)
    data_norm = (data - data_means)/data_std
    cov_mat = np.cov(data_norm , rowvar = False)
    eigen_values , eigen_vectors = np.linalg.eigh(cov_mat)
    
    sorted_idx = np.argsort(eigen_values)[::-1]
    sorted_eigenvalues = eigen_values[sorted_idx]
    sorted_eigenvectors = eigen_vectors[:,sorted_idx]
    
    return sorted_eigenvalues, sorted_eigenvectors, data_means, data_std


''' Projects data after decomposition
    :param data: Numpy array, containing our data, with columns as the dimensions.
    :param eigenvectors: The eigenvectors we are projecting to.
    :return: The data, projected onto the eigenvector representation.
'''
def invert_pca(data, eigenvectors):
    means = np.mean(data, axis = 0)
    std = np.std(data, axis = 0)
    return np.dot(eigenvectors.transpose(), np.dot(eigenvectors,((data - means)/std).transpose())).transpose()*std + means


''' Removes outliers, based on the interquartile range method along multiple features
    :param df: The DataFrame containing our data
    :param list_of_features: A list of features to consider removing outliers on
    :return: Cleaned up data
'''
def remove_outliers(df, list_of_features):
    conditions = np.full(len(df), True)
    for feature in list_of_features:
        quantiles = np.quantile(df[feature], [0.25, 0.75])
        iqr = quantiles[1] - quantiles[0]
        # Calculate the allowed range
        lower_bound = quantiles[0] - 1.5*iqr
        upper_bound = quantiles[1] + 1.5*iqr
        # Add the new condition to the global one
        conditions = conditions & ((df[feature] <= upper_bound) & (df[feature] >= lower_bound))
    return df[conditions]

''' One-Hot encodes a particular feature.
    :param df: The DataFrame containing our data
    :param feature: The feature to encode
    :return: The DataFrame with the new columns, corresponding to the encoding
'''
def do_one_hot_encoding(df, feature):
    # For each feature value, creates a new column with the encoding
    for feature_type in df[feature].unique():
        encoding_name = 'is_' + str(feature) + '_' + str(feature_type)
        df[encoding_name] = np.where(df[feature] == feature_type, 1, 0)
    return df

''' Imputes missing value based on median
    :param df: The DataFrame containing our data
    :param list_of_features: A list of features to consider for imputation
    :return: The DataFrame with the required values imputed
'''
def mean_imputer(df, list_of_features):
    for feature in list_of_features:
        median = df[feature].median()
        df[feature] = np.where(df[feature].isna(), median, df[feature])
    return df