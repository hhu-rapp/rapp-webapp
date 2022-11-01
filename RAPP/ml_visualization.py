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
class QueryMetastats:
    """ A class containing metastats for query results.

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


class Query:
    """ A class handling queries.

    Attributes
    ----------
    fp: str
        The relative filepath to the file the sql query can be found in.
    metastats: QueryMetastats | None
        The metastats for query results.
    name: str
        The name of the query.
    results: pandas.Dataframe | None
        A pandas dataframe containing the query results.
    _query: str
        The query in use.
    """

    def __init__(self, name: str) -> None:
        self.results: pd.DataFrame | None = None
        self.name: str = name
        self._query: str = self._get_query()

    def __repr__(self) -> str:
        return f"Query({self.name})"

    def _get_query(self) -> str:
        """Read query from file."""
        with open(self.get_fp()) as file:
            return file.read()

    def execute_query(self, db_uri: str) -> None:
        """Execute query on given database.

        Parameters
        ----------
        db_uri : str
            The URI of the database the query will be executed on.
        """
        engine = db.create_engine(db_uri)
        with engine.connect() as conn:
            # TODO: check for valid query?
            query = db.text(self._query)
            self.results = pd.DataFrame(conn.execute(query).fetchall())

    def get_fp(self) -> str:
        """Return relative filepath to file containing sql query."""
        return path.join(
            current_app.config['MODELS_PATH'],
            self.name,
            current_app.config['QUERY_FILENAME']
        )

    def get_metastats(self) -> QueryMetastats | None:
        """Return metastats for query results."""
        if self.results is None:
            return None

        return QueryMetastats(
            num_samples=len(self.results),
            num_feats=len(self.results.columns),
            num_miss_vals=self.results.isna().sum().sum()
        )


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
    form_query.edit_queries(get_query_options())

    query: Query | None = None
    if form_query.query.data and form_query.validate_on_submit() and db_uri:
        query = Query(name=form_query.query.data)
        query.execute_query(db_uri)

        session['query_name'] = query.name

    return render_template(
        'ml_visualization/index.html',
        ml_db_filename=session.get('ml_db_filename'),
        query_name=session.get('query_name'),
        form_db=form_db,
        form_query=form_query,
        metastats=query.get_metastats() if query else None
    )
