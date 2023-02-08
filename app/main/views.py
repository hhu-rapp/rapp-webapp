import pandas as pd
import sqlalchemy
from joblib import load

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename


from . import main
from .forms import (DatabaseForm, NewsForm, PasswordChangeForm, RegisterForm,
                    QueryForm, UserEditAdminForm, ModelForm)
from ..decorators import admin_required
from ..email import send_email
from ..models import MLDatabase, Model, News, Query, User
from ml_backend import pipeline


@main.route('/')
def index():
    news: News = News.query.order_by(News.timestamp.desc()).all()
    return render_template('main/index.html', news=news)


@main.route('/admin/news')
@admin_required
def news():
    news: News = News.query.order_by(News.timestamp.desc()).all()
    return render_template('main/news.html', news=news)


@main.route('/news/add', methods=['GET', 'POST'])
@admin_required
def add_news():
    form: NewsForm = NewsForm()
    if form.validate_on_submit():
        news_post = News(
            title=form.title.data,
            text=form.text.data,
            author_id=current_user.id       # type: ignore
        )
        news_post.save()
        flash('New post has been added.')
        return redirect(url_for('main.news'))
    return render_template('main/add_news.html', form=form)


@main.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
@admin_required
def edit_news(news_id: int):
    news_post: News = News.query.get_or_404(news_id)
    form: NewsForm = NewsForm()

    if form.validate_on_submit():
        news_post.title = form.title.data
        news_post.text = form.text.data

        news_post.save()
        flash('News Post has been updated.')
        return redirect(url_for('main.edit_news', news_id=news_id))
    form.title.data = news_post.title
    form.text.data = news_post.text

    return render_template('main/edit_news.html', form=form)


@main.route('/news/delete/<int:news_id>')
@admin_required
def delete_news(news_id: int):
    news_post: News = News.query.get_or_404(news_id)
    news_post.delete()
    return redirect(url_for('main.news'))


@main.route('/ml_database/<int:id>')
@login_required
def ml_database(id: int):
    ml_database: MLDatabase = MLDatabase.query.get_or_404(id)

    if ml_database.user_id != current_user.id:      # type: ignore
        abort(403)

    return render_template(
        'main/ml_database.html',
        queries=ml_database.queries
    )


@main.route('/ml_database/add', methods=['GET', 'POST'])
@login_required
def add_ml_database():
    form: DatabaseForm = DatabaseForm()
    if form.validate_on_submit():
        name: str = form.name.data
        user_id: int = current_user.id      # type: ignore

        filename = secure_filename(form.file.data.filename or '')
        if not filename:
            abort(500)
        unique_filename: str = uuid4().__str__() + filename
        form.file.data.save(
            Path(current_app.config['UPLOAD_FOLDER']) / unique_filename)

        ml_database: MLDatabase = MLDatabase(
            name=name,
            filename=unique_filename,
            user_id=user_id
        )
        ml_database.save()
        flash('ML-Database has been uploaded.')
        return redirect(url_for('main.manage_ml_databases'))
    return render_template('main/add_ml_database.html', form=form)


@main.route('/ml_database/delete/<int:id>')
@login_required
def delete_ml_database(id: int):
    ml_database: MLDatabase = MLDatabase.query.get_or_404(id)

    if ml_database.user_id != current_user.id or not current_user.is_admin:   # type: ignore
        abort(403)

    ml_database.delete()
    flash('ML-Database has been deleted.')
    return redirect(url_for('main.manage_ml_databases'))


@main.route('/admin')
@admin_required
def admin():
    return render_template('main/admin.html')


@main.route('/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('main/manage_users.html', users=users)


@main.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = RegisterForm()

    if form.validate_on_submit():
        password = User.generate_password()
        user = User(
            email=form.email.data,
            password=password
        )       # type: ignore
        user.save()

        send_email(
            to=user.email,
            subject='Registration Confirmation',
            template='main/email/registration',
            email=user.email,
            password=password
        )
        flash(f'{user.email} has been added as a User.')

        return redirect(url_for('main.manage_users'))
    return render_template('main/add_user.html', form=form)


@main.route('/user/<int:id>')
@admin_required
def show_user(id: int):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('main/show_user.html', user=user)


@main.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id: int):
    user = User.query.get_or_404(id)
    form = UserEditAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        print(form.email.data)
        print(user.email)
        user.save()
        flash(f'User ID:{user.id} has been updated.')
        return redirect(url_for('main.show_user', id=user.id))
    form.email.data = user.email
    return render_template('main/edit_user.html', form=form, user=user)


@main.route('/user/delete/<int:id>')
@admin_required
def delete_user(id: int):
    user = User.query.get_or_404(id)

    if user.is_admin:
        abort(403)

    user.delete()
    return redirect(url_for('main.manage_users'))


@main.route('/home')
@login_required
def home():
    ml_databases = current_user.ml_databases    # type: ignore
    return render_template(
        'main/home.html',
        ml_databases=ml_databases
    )


@main.route('/machine-learning/<int:db_id>')
@login_required
def select_prediction_query(db_id):
    queries = Query.query.all()
    return render_template(
        'main/machine_learning_query_selection.html',
        queries=queries,
        db_id=db_id
    )


@main.route('/machine-learning/<int:db_id>/<int:query_id>')
@login_required
def data(db_id, query_id):
    db = MLDatabase.query.get_or_404(db_id)
    query = Query.query.get_or_404(query_id)

    if db.user_id != current_user.id or not current_user.is_admin:
        abort(403)

    # TODO remove hardcoded sqlite
    db_uri = 'sqlite:///' + current_app.config['UPLOAD_FOLDER'] + '/' + db.filename
    engine = sqlalchemy.create_engine(db_uri)
    with engine.connect() as conn:
        query_string = sqlalchemy.text(query.query_string)
        df = pd.DataFrame(conn.execute(query_string).fetchall())

    return render_template('main/machine-learning.html', df=df)


@main.route('/prediction/<int:db_id>/<int:query_id>/<int:model_id>')
@login_required
def prediction(db_id, query_id, model_id):
    db = MLDatabase.query.get_or_404(db_id)
    query = Query.query.get_or_404(query_id)
    model = Model.query.get_or_404(model_id)

    if db.user_id != current_user.id or not current_user.is_admin:
        abort(403)

    # TODO: remove hardcoded sqlite
    db_uri = 'sqlite:///' + current_app.config['UPLOAD_FOLDER'] + '/' + db.filename
    engine = sqlalchemy.create_engine(db_uri)
    with engine.connect() as conn:
        query_string = sqlalchemy.text(query.query_string)
        df = pd.DataFrame(conn.execute(query_string).fetchall())
        
    estimator = load(model.filename)['model']
    
    pred_df = pipeline.prediction(estimator, df, query.name)

    return render_template('main/machine-learning.html', df=df)


@main.route('/reset_password/<int:id>')
@login_required
def reset_password(id):
    user = User.query.get_or_404(id)
    password = User.generate_password()
    user.password = password
    user.save()
    send_email(
        to=user.email,
        subject='Password Reset',
        template='main/email/registration',
        email=user.email,
        password=password
    )
    flash('Password has been changed.')
    return redirect(url_for('main.edit_user', id=id))


@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            current_user.save()     # type: ignore
            flash('Password has been updated.')
            return redirect(url_for('main.profile'))
        flash('Wrong password.')
    return render_template('main/change_password.html', form=form)


@main.route('/queries')
@admin_required
def manage_queries():
    queries = Query.query.order_by(Query.id.asc()).all()
    return render_template('main/manage_queries.html', queries=queries)


@main.route('/query/add', methods=['GET', 'POST'])
@admin_required
def add_query():
    form = QueryForm()
    if form.validate_on_submit():
        query = Query(
            name=form.name.data,
            query_string=form.query_string.data
        )
        query.save()
        flash("New query has been added.")
        return redirect(url_for('main.manage_queries'))
    return render_template('main/add_query.html', form=form)


@main.route('/query/delete/<int:id>')
@admin_required
def delete_query(id):
    query = Query.query.get_or_404(id)
    query.delete()
    return redirect(url_for('main.manage_queries'))


@main.route('/query/<int:id>')
@admin_required
def show_query(id):
    query = Query.query.get_or_404(id)
    return render_template('main/show_query.html', query=query)


@main.route("/query/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def edit_query(id):
    form = QueryForm()
    query = Query.query.get_or_404(id)

    if form.validate_on_submit():
        query.name = form.name.data
        query.query_string = form.query_string.data
        query.save()
        flash('Query has been updated.')
        return redirect(url_for('main.edit_query', id=id))

    form.name.data = query.name
    form.query_string.data = query.query_string

    return render_template('main/edit_query.html', form=form)


@main.route('/models/')
@admin_required
def manage_models():
    models = Model.query.all()
    return render_template('main/manage_models.html', models=models)


@main.route('/model/add', methods=['GET', 'POST'])
@admin_required
def add_model():
    # TODO: DELETE FOR PRODUCTION
    # including Form + Template + Link in manage_models.html
    form = ModelForm()
    if form.validate_on_submit():
        filename = secure_filename(form.model_file.data.filename or '')
        if not filename:
            abort(500)
        unique_filename: str = uuid4().__str__() + filename
        form.model_file.data.save(
            Path(current_app.config['UPLOAD_FOLDER']) / unique_filename)

        model = Model(        # type: ignore
            name=form.name.data,
            filename=unique_filename
        )
        model.save()
        flash('Model added.')
        return redirect(url_for('main.manage_models'))
    return render_template('main/add_model.html', form=form)


@main.route('/ml_databases')
@login_required
def manage_ml_databases():
    ml_databases = current_user.ml_databases    # type: ignore
    return render_template(
        'main/manage_ml_databases.html',
        ml_databases=ml_databases
    )
