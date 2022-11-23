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
from .forms import ModelSelectForm
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
    name: str
        The name of the query.
    results: pandas.Dataframe | None
        A pandas dataframe containing the query results.
    """

    def __init__(self, name: str) -> None:
        self.results: pd.DataFrame | None = None
        self.name: str = name
        self._query: str = self._get_query()

    def __repr__(self) -> str:
        return f"Query({self.name})"

    def _get_query(self) -> str:
        """Read query from file."""
        filename: str = path.join(
            self.get_fp(),
            current_app.config['QUERY_FILENAME']
        )
        with open(filename) as file:
            return file.read()

    @staticmethod
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
        """Return relative filepath to folder containing
        model and sql files.
        """
        return path.join(
            current_app.config['MODELS_PATH'],
            self.name
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

    def get_model_options(self) -> list[tuple[str, str]]:
        """Return a list of available models for query."""
        fileformat = current_app.config.get('MODEL_FILEFORMAT', '')
        model_options: list[tuple[str, str]] = []
        for file in listdir(self.get_fp()):
            if file.endswith(fileformat):
                model_options.append((file, file[:-len(fileformat)]))
        return model_options


class DatabaseML:
    """A class managing the database for machine learning."""
    DB_UPLOAD_FOLDER: str = 'databases'

    def __init__(self,
                 db_type: str,
                 filename: str | None,
                 upload_folder: str) -> None:
        """Init DatabaseML.

        Parameters
        ----------
        db_type: str
            The type of the database used for machine learning.
            (e.g. sqlite)
        filename: str | None
            The name of the database file.
        upload_folder: str
            The name of the upload folder.
        """
        self.db_type: str = db_type
        self.filename: str | None = filename
        self.upload_folder: str = upload_folder

    def __repr__(self) -> str:
        return f"DatabaseML({self.filename})"

    def get_db_filepath(self) -> str:
        """Create and return a secure filepath to database file from filename.

        Raises
        ------
        TypeError:
            If filename does not exist.
        """
        if self.filename is None:
            raise TypeError

        return path.join(
            self.upload_folder,
            self.DB_UPLOAD_FOLDER,
            secure_filename(self.filename)
        )

    def get_ml_db_uri(self) -> str:
        """Create and return database URI."""
        db_filepath: str = self.get_db_filepath()
        return (self.db_type + ':///' + db_filepath)

    def upload_database(self, file: FileStorage) -> None:
        """Upload database.

        Parameters
        ----------
        file: werkzeug.datastructures.FileStorage
            The database file to be uploaded.
        """
        if file.filename:
            self.filename = file.filename
            fp: str = self.get_db_filepath()
            file.save(fp)


class Model:
    """A class managing models."""
    def __init__(self, filepath: str, fileformat: str) -> None:
        """Init Model

        Parameters
        ----------
        filepath: str
            The filepath the model can be loaded from.
        fileformat: str
            The format of the file the model is stored in.
        """
        self.filepath: str = filepath
        self.fileformat: str = fileformat

    def __repr__(self) -> str:
        return f"Model({self.filepath})"

    def get_model_name(self) -> str:
        """Return model name."""
        return self.filepath[:-len(self.fileformat)]


@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ml_db_filename: str | None = session.get('ml_db_filename')
    database_ml: DatabaseML = DatabaseML(
        db_type=current_app.config.get('ML_DB_TYPE', ''),
        filename=ml_db_filename,
        upload_folder=current_app.config.get('UPLOAD_FOLDER', '')
    )

    # DATABASE FORM
    form_db: DatabaseUploadForm = DatabaseUploadForm()
    if form_db.ml_db_file.data and form_db.validate_on_submit():
        database_ml.upload_database(form_db.ml_db_file.data)
        session['ml_db_filename'] = database_ml.filename
        if session.get('query_name'):
            session.pop('query_name')
        if session.get('model_filepath'):
            session.pop('model_filepath')

    # QUERY FORM
    form_query: QuerySelectForm = QuerySelectForm()
    form_query.edit_queries(Query.get_query_options())
    if form_query.query.data and form_query.validate_on_submit():
        session['query_name'] = form_query.query.data
        if session.get('model_filepath'):
            session.pop('model_filepath')

    query: Query | None = None
    metastats: QueryMetastats | None = None
    query_name = session.get('query_name')
    if query_name:
        query = Query(name=query_name)
        query.execute_query(database_ml.get_ml_db_uri())
        metastats = query.get_metastats()

    df: pd.DataFrame = pd.DataFrame()
    if query and query.results is not None:
        df = query.results

    # MODEL FORM
    form_model: ModelSelectForm = ModelSelectForm()
    model: Model | None = None
    if query:
        form_model.edit_models(query.get_model_options())

    if form_model.model.data and form_model.validate_on_submit():
        session['model_filepath'] = form_model.model.data

    model_filepath: str | None = session.get('model_filepath')
    if model_filepath:
        model = Model(
            filepath=model_filepath,
            fileformat=current_app.config.get('MODEL_FILEFORMAT', '')
        )

    return render_template(
        'ml_visualization/index.html',
        ml_db_filename=session.get('ml_db_filename'),
        query_name=session.get('query_name'),
        model_name=model.get_model_name() if model else None,
        form_db=form_db,
        form_query=form_query,
        form_model=form_model,
        metastats=metastats,
        df=df
    )
