from flask import Blueprint
from flask import current_app
from flask import render_template
from flask_login import login_required
from os import path
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .forms import DatabaseUploadForm

bp = Blueprint('ml_visualization', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form_db: DatabaseUploadForm = DatabaseUploadForm()
    file_db: FileStorage | None = None

    if form_db.validate_on_submit():
        file_db = form_db.file_db.data

        if file_db.filename:
            filepath_db = path.join(
                current_app.config['UPLOAD_PATH'],
                'databases',
                secure_filename(file_db.filename)
            )
            file_db.save(filepath_db)

    return render_template(
        'ml_visualization/index.html',
        form_db=form_db,
        file_db=file_db
    )
