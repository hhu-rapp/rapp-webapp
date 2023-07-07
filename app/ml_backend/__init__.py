import pandas as pd
import sqlalchemy
from flask import current_app
from ..models import MLDatabase, Query


# get data from the database
def query_database(db, query):
    """
    Returns the loaded features and target variable from the database.

    Parameters
    ----------
    db : MLDatabase
        Database to be queried.
    query : Query (Features)
        Query to be executed.

    Returns
    -------
    df : Dataframe
        Dataframe containing the features and target variable.
    """

    # TODO: remove hardcoded sqlite
    db_uri = 'sqlite:///' + current_app.config['UPLOAD_FOLDER'] + '/' + db.filename
    engine = sqlalchemy.create_engine(db_uri)
    with engine.connect() as conn:
        if isinstance(query, str):
            query_string = sqlalchemy.text(query)
        else:
            query_string = sqlalchemy.text(query.query_string)
        df = pd.DataFrame(conn.execute(query_string).fetchall())

    return df


def highlight_greaterthan(s, threshold_val, column):
    """
    Highlights values greater than threshold_val in a Series green, and red otherwise.

    Parameters
    ----------
    s : Series
        Data to be highlighted.
    threshold_val : float
        Value to be compared against.
    column : str
        Column to be highlighted.
    """
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] >= threshold_val
    return ['border-top: 0.5pt solid silver; background-color: rgba(255, 0, 0, 0.25)' if is_max.any()
            else 'border-top: 0.5pt solid silver; background-color: rgba(0, 200, 0, 0.15)' for v in is_max]
