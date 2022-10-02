from flask import Blueprint
from flask import render_template

bp = Blueprint('ml_visualization', __name__)


@bp.route('/')
def home():
    return render_template('ml_visualization/index.html')
