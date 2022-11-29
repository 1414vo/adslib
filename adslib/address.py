import numpy as np
import statsmodels.api as sm
from sklearn.model_selection import train_test_split, KFold

def mse(predictions, target):
    return (predictions - target)**2 / len(predictions)
    
def cross_validation(features, target, split_fractions, loss = mse,  number_of_splits = 5, alpha = 0):
    assert len(split_fractions) == 3, "'split_fractions' parameter should contain 3 numbers, ['fit_fraction', 'validation_fraction', 'test_fraction']."
    assert sum(split_fractions) == 1, "Fractions should add up to 1."
    
    X_fit_val , X_test, y_fit_val, y_test = train_test_split(features, target, test_size=split_fractions[2])
    
    kfold = KFold(n_splits=number_of_splits)
    scores = []
    for fit_index, val_index in kfold.split(X_fit_val):
        X_fit = X_fit_val.iloc[fit_index]
        X_val = X_fit_val.iloc[val_index]
        y_fit = y_fit_val.iloc[fit_index]
        y_val = y_fit_val.iloc[val_index]
        
        model = sm.OLS(y_fit, X_fit)
        # Ridge regression due to multicollinearity
        fit = model.fit_regularized(alpha = alpha, L1_wt = 0)
        scores.append(loss(fit.predict(X_val), y_val))
    
    test_model = sm.OLS(y_fit_val, X_fit_val)
    test_fit = test_model.fit_regularized(alpha = alpha, L1_wt = 0)
    
    results = {}
    results['validation_scores'] = np.array(scores)
    results['test_score'] = loss(test_fit.predict(X_test), y_test)
    results['summary_frame'] = test_fit.predict(X_test).summary_grame(alpha = 0.05)
    return results, test_model

