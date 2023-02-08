import pandas as pd


def preprocess_data(X):
    """
    Preprocesses X data.

    Parameters
    ----------
    X : Dataframe

    Returns
    -------
    X : Dataframe
        Preprocessed X data.
    """
    categorical = X.select_dtypes(exclude=["number"]).columns
    
    # Adapt to categorical data.
    if len(categorical) > 0:
        one_hot = pd.get_dummies(data=X[categorical], columns=categorical)
        X = pd.concat([X, one_hot], axis=1)
        # Remove old categorical attributes from input features
        X = X.drop(categorical, axis=1)

    return X


def predict(model, X, label):
    """
    Predicts on X data.

    Parameters
    ----------
    model : scikit estimator
        Model to be used for prediction.
    X : Dataframe
        Data to be predicted on.
    label : str
        Target variable to be predicted on in X.
    """
    if label in X.columns:
        X.drop(labels=label, axis=1, inplace=True)

    X = preprocess_data(X)
    
    # 1 is the worst case outcome for the target variable
    X['Prediction'] = model.predict_proba(X)[:, 1]
    
    return X
    
    
def threshold(proba, value=0.80):
    """
    Returns threshold for prediction.
    
    Parameters
    ----------
    proba : (n_samples, 1)
        Probability to be used as threshold.
    value : float
        Value to be used as threshold.
    """
    return proba >= value