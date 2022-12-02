import numpy as np
import statsmodels.api as sm
from sklearn.model_selection import train_test_split, KFold

''' Define the default loss function as Mean-Squared Error.
    :param predictions: Predictions made by model
    :param target: Ground truth for the target variable
    :return: Mean-Squared error of predictions vs target
'''
def mse(predictions, target):
    return sum((predictions - target)**2 / len(predictions))
    
''' Train and validate the model through k-fold cross-validation.
    :param features: The features of the dataset
    :param target: Ground truth for the target variable
    :param split_fractions: A list of 3 number, describing the proportions of the training, validation and test sets
    :param loss: The loss function to be used for evaluation
    :param number_of_splits: Specifies the number of iterations k for the k-fold cross-validation method
    :param alpha: The penalty coefficient for the regularization
    :L1_wt: The parameter used for describing the elastic net - 0 means we have a Ridge Regression, while 1 means we are using a Lasso Regularisation
    :return: A result summary from the validation and test, including the trained model
''' 
def cross_validation_train(features, target, split_fractions, loss = mse,  number_of_splits = 5, alpha = 0, L1_wt = 0):
    assert len(split_fractions) == 3, "'split_fractions' parameter should contain 3 numbers, ['fit_fraction', 'validation_fraction', 'test_fraction']."
    assert sum(split_fractions) == 1, "Fractions should add up to 1."
    
    # Split dataset in 2 sub-datasets - one for cross-validation, and one for testing
    X_fit_val , X_test, y_fit_val, y_test = train_test_split(features, target, test_size=split_fractions[2])
    
    kfold = KFold(n_splits=number_of_splits)
    scores = []
    
    # Perform k-fold cross-validation
    for fit_index, val_index in kfold.split(X_fit_val):
        X_fit = X_fit_val[fit_index]
        X_val = X_fit_val[val_index]
        y_fit = y_fit_val[fit_index]
        y_val = y_fit_val[val_index]
        
        model = sm.OLS(y_fit, X_fit)
        
        fit = model.fit_regularized(alpha = alpha, L1_wt = L1_wt)
        scores.append(loss(fit.predict(X_val), y_val))
    
    # Fit on test model
    test_model = sm.OLS(y_fit_val, X_fit_val)
    test_fit = test_model.fit_regularized(alpha = alpha, L1_wt = L1_wt)
    
    # Report results
    results = {}
    results['validation_scores'] = np.array(scores)
    results['test_score'] = loss(test_fit.predict(X_test), y_test)

    return results, test_fit

