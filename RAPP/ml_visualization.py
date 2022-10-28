import pandas as pd
import sqlalchemy as db

from dataclasses import dataclass
from flask import Blueprint
from flask import current_app
from flask import session
from flask import render_template
from flask_login import login_required
from os import listdir
from os import path
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .forms import DatabaseUploadForm
from .forms import QuerySelectForm

bp = Blueprint('ml_visualization', __name__)


@dataclass
class MetastatsQuery:
    """ Query Metastats

    Attributes
    ----------
    num_samples : int
        The number of samples in loaded query.
    num_feats : int
        The number of features in loaded query.
    num_miss_vals : int
        The sum of NA values in loaded query.
    """
    num_samples: int
    num_feats: int
    num_miss_vals: int


def create_ml_db_filepath(filename: str) -> str:
    """Create a secure filepath to database upload folder from filename.

    Parameters
    ----------
    filename : str
        The filename of uploaded database.

    Returns
    -------
    str
        A secure filepath to database upload folder.
    """

    return path.join(
        current_app.config['UPLOAD_PATH'],
        'databases',
        secure_filename(filename)
    )


def get_query_options() -> list[tuple[str, str]]:
    """Return a list of available sql queries."""
    # TODO: refactor
    query_options: list[tuple[str, str]] = []
    models_root: str = current_app.config['MODELS_PATH']

    for features_folder in listdir(models_root):
        features_folder_fp = path.join(models_root, features_folder)
        for labels_folder in listdir(features_folder_fp):
            query_name: str = path.join(
                features_folder,
                labels_folder
            )
            query_option: tuple[str, str] = (query_name, query_name)
            query_options.append(query_option)

    return query_options


def run_query(db_uri: str, query_fp: str) -> list[db.engine.Row]:
    """Execute sql query from file found at given filepath.

    Parameters
    ----------
    db_uri : str
        The URI of the database the query will be executed on.
    query_fp : str
        The filepath to the sql file containing the query.

    Returns
    -------
    list[sqlalchemy.engine.Row]
        A result of the executed sql query on the selected database as list of
        rows.
    """

    engine = db.create_engine(db_uri)
    with engine.connect() as conn:
        with open(query_fp) as file:
            query = db.text(file.read())
            return conn.execute(query).fetchall()


def upload_database(file: FileStorage) -> None:
    """Upload database.

    Parameters
    ----------
    file: werkzeug.datastructures.FileStorage
        The database file to be uploaded.
    """

    if file.filename:
        fp: str = create_ml_db_filepath(file.filename)
        file.save(fp)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    db_uri: str | None = None
    if session.get('ml_db_filename'):
        db_uri = (current_app.config.get('ML_DB_TYPE', '') + ':///'
                  + create_ml_db_filepath(session['ml_db_filename']))

    form_db: DatabaseUploadForm = DatabaseUploadForm()
    if form_db.ml_db_file.data and form_db.validate_on_submit():
        upload_database(form_db.ml_db_file.data)

        if session.get('query_name'):
            session.pop('query_name')

        session['ml_db_filename'] = form_db.ml_db_file.data.filename

    form_query: QuerySelectForm = QuerySelectForm()

    query_options: list[tuple[str, str]] = get_query_options()
    form_query.edit_queries(query_options)

    metastats: MetastatsQuery | None = None
    df: pd.DataFrame | None = None

    if form_query.query.data and form_query.validate_on_submit() and db_uri:
        query_name: str = form_query.query.data

        if query_name:
            QUERY_FILENAME: str = 'query.sql'

            query_fp: str = path.join(
                current_app.config['MODELS_PATH'],
                query_name,
                QUERY_FILENAME
            )

            query_results: list[db.engine.Row] = run_query(db_uri, query_fp)

            session['query_name'] = query_name

            df = pd.DataFrame(query_results)
            metastats = MetastatsQuery(
                num_samples=len(df),
                num_feats=len(df.columns),
                num_miss_vals=df.isna().sum().sum()
            )

    return render_template(
        'ml_visualization/index.html',
        ml_db_filename=session.get('ml_db_filename'),
        query_name=session.get('query_name'),
        form_db=form_db,
        form_query=form_query,
        metastats=metastats
    )
