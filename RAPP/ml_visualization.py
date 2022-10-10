from flask import Blueprint
from flask import render_template
from flask_login import login_required

bp = Blueprint('ml_visualization', __name__)


@bp.route('/')
@login_required
def home():
    return render_template('ml_visualization/index.html')
