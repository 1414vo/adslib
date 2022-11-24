import numpy as np
import statsmodels.api as sm
from sklearn.model_selection import train_test_split, KFold

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
    
def cross_validation(features, target, split_fractions, loss = mse,  number_of_splits = 5, alpha = 0):
    assert len(split_fractions) == 3, "'split_fractions' parameter should contain 3 numbers, ['fit_fraction', 'validation_fraction', 'test_fraction']."
    assert sum(split_fractions) == 1, "Fractions should add up to 1."
    
    X_fit_val , X_test, y_fit_val, y_test = train_test_split(features, target, test_size=split_fractions[2])
    
    kfold = KFold(n_splits=number_of_splits)
    scores = []
    for fit_index, val_index in kfold.split(X_fit_val):
        X_fit = X_fit_val[fit_index]
        X_val = X_fit_val[val_index]
        y_fit = y_fit_val[fit_index]
        y_val = y_fit_val[val_index]
        
        model = sm.OLS(y_fit, X_fit)
        # Ridge regression due to multicollinearity
        fit = model.fit_regularized(alpha = alpha, L1_wt = 0)
        scores.append(loss(fit.get_prediction(X_val), y_val))
    
    test_model = sm.OLS(y_fit_val, X_fit_val)
    test_fit = test_model.fit_regularized(alpha = alpha, L1_wt = 0)
    
    results = {}
    results['validation_scores'] = np.array(scores)
    results['test_score'] = loss(test_fit.get_prediction(X_test), y_test)
    results['summary_frame'] = loss(test_fit.get_prediction(X_test).summary_grame(alpha = 0.05))
    return results

def mse(predictions, target):
    return (predictions - target)**2 / len(predictions)