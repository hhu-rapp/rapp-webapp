import pandas as pd
import sqlalchemy
from joblib import load
import json

from flask import abort, current_app, flash, redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename

from . import main
from .forms import (DatabaseForm, NewsForm, PasswordChangeForm, RegisterForm,
                    QueryForm, UserEditAdminForm, ModelForm)
from ..decorators import admin_required
from ..email import send_email
from ..ml_backend.dummy_data import generate_performance_history, generate_risk_analysis
from ..models import MLDatabase, Model, News, Query, User
from ..ml_backend import pipeline, highlight_greaterthan, query_database


@main.route('/')
@login_required
def index():
    page_title = "Dashboard"
    news: News = News.query.order_by(News.timestamp.desc()).all()

    notifications = [{"link": '/prediction/1/1/1', "title": 'New Prediction', "mins_ago": 10}, {"link": '/performance_history', "title": 'New Performance History', "mins_ago": 15}]
    majors = ['Informatik', 'Sozialwissenschaften', 'Wirtschaftswissenschaften', 'Rechtswissenschaften']
    return render_template('main/dashboard.html', news=news, notifications=notifications, page_title=page_title,
                           majors=majors)


# Ajax call for the dashboard
@main.route('/dashboard-data/<string:major_id>/<string:degree_id>')
@login_required
def dashboard_data(major_id, degree_id):
    # generate dummy performance data
    performance_df = generate_performance_history(200)
    # generate dummy risk analysis data
    dropout_df = generate_risk_analysis(200)

    avg_bachelor_semesters = None
    avg_master_semesters = None

    if major_id == 'all':
        performance_df = performance_df
        dropout_df = dropout_df
    else:
        performance_df = performance_df[performance_df['Major'] == major_id]
        dropout_df = dropout_df[dropout_df['Major'] == major_id]

    if degree_id == 'Bachelor':
        performance_df = performance_df[performance_df['Degree'] == 'Bachelor']
        dropout_df = dropout_df[dropout_df['Degree'] == 'Bachelor']

    elif degree_id == 'Master':
        performance_df = performance_df[performance_df['Degree'] == 'Master']
        dropout_df = dropout_df[dropout_df['Degree'] == 'Master']

    # get total number of students
    total_students = len(performance_df['Matrikel_Nummer'].unique())
    # get total number of dropouts
    total_dropouts = len(dropout_df[dropout_df['Dropout'] == 'Yes'])

    # avg number of semesters for all students
    # group by student id and get sum of ECTS, max number of semesters and degree
    group_performance = performance_df.groupby('Matrikel_Nummer').agg(
        {'ECTS': 'sum', 'Num_Semester': 'max', 'Degree': 'max'}).reset_index()

    if degree_id != 'Master':
        # get students that have 180 ECTS and are in bachelor
        bachelor_students = group_performance[
            (group_performance['ECTS'] >= 180) & (group_performance['Degree'] == 'Bachelor')]
        # get avg number of semesters for bachelor students
        avg_bachelor_semesters = round(bachelor_students['Num_Semester'].mean(), 0)

    if degree_id != 'Bachelor':
        # get students that have 120 ECTS and are in master
        master_students = group_performance[
            (group_performance['ECTS'] >= 120) & (group_performance['Degree'] == 'Master')]
        # get avg number of semesters for master students
        avg_master_semesters = round(master_students['Num_Semester'].mean(), 0)

    # avg ects per semester
    group_performance = performance_df.groupby(['Semester', 'Year']).agg(
        {'ECTS': 'sum'}).reset_index()
    avg_ects_per_semester = round(group_performance['ECTS'].mean(), 0)

    # get data for plots get only unique Matrikel_Nummer
    group_performance = performance_df.groupby('Matrikel_Nummer').agg({'Sex': 'max', 'Nationality': 'max'}).reset_index()
    sex_plot = group_performance['Sex'].value_counts().reset_index().sort_values(by='Sex', ascending=False).to_dict(
        'list')

    nat_plot = group_performance['Nationality'].value_counts().reset_index().sort_values(by='Nationality',
                                                                                         ascending=False).to_dict(
        'list')

    # add all values to response
    response = {'totalStudents': total_students,
                'totalDropouts': total_dropouts,
                'avgBachelorSemesters': avg_bachelor_semesters,
                'avgMasterSemesters': avg_master_semesters,
                'avgEctsPerSemester': avg_ects_per_semester,
                'sexPlot': sex_plot,
                'natPlot': nat_plot}

    response = json.dumps(response)

    return jsonify(response)


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
            author_id=current_user.id  # type: ignore
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

    if ml_database.user_id != current_user.id:  # type: ignore
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
        user_id: int = current_user.id  # type: ignore

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

    if ml_database.user_id != current_user.id or not current_user.is_admin:  # type: ignore
        abort(403)

    ml_database.delete()
    flash('ML-Database has been deleted.')
    return redirect(url_for('main.manage_ml_databases'))


@main.route('/admin')
@admin_required
def admin():
    page_title = "Admin Panel"
    return render_template('main/admin.html', page_title=page_title)


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
        )  # type: ignore
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
    ml_databases = current_user.ml_databases  # type: ignore
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

    return render_template('main/machine-learning.html', styled_df=df.style)


@main.route('/prediction/<int:db_id>/<int:query_id>/<int:model_id>')
@login_required
def prediction(db_id, query_id, model_id):
    page_title = "Student Predictions"

    db = MLDatabase.query.get_or_404(db_id)
    query = Query.query.get_or_404(query_id)
    model = Model.query.get_or_404(model_id)

    if db.user_id != current_user.id or not current_user.is_admin:
        abort(403)

    df = query_database(db, query)
    label = query.name

    estimator = load(current_app.config['UPLOAD_FOLDER'] + '/' + model.filename)['model']
    pred_df = pipeline.predict(estimator, df, label)

    styled_df = df.style.apply(highlight_greaterthan, threshold_val=0.8, column=[pred_df.columns[-1]], axis=1)

    return render_template('main/machine-learning.html', styled_df=styled_df, features=pred_df.columns[:-1], page_title=page_title)


@main.route('/group_level_prediction/<int:db_id>/<int:query_id>/<int:model_id>')
@login_required
def group_prediction(db_id, query_id, model_id):
    aggregations = {
        'Average': 'mean',
        'Count': 'count',
        'Sum': 'sum',
        'Maximum': 'max',
        'Minimum': 'min'
    }
    db = MLDatabase.query.get_or_404(db_id)
    query = Query.query.get_or_404(query_id)
    model = Model.query.get_or_404(model_id)

    if db.user_id != current_user.id or not current_user.is_admin:
        abort(403)

    df = query_database(db, query)
    label = query.name

    estimator = load(current_app.config['UPLOAD_FOLDER'] + '/' + model.filename)['model']
    pred_df = pipeline.predict(estimator, df, label)

    group = request.args.get('feature', None)
    agg = request.args.get('aggregation', 'Average')

    if group not in pred_df.columns:
        group = pred_df.columns[0]
    if agg.strip('\n') not in aggregations.keys():
        agg = 'Average'

    pred_df = pred_df.groupby(by=group, dropna=False).agg(aggregations[agg])

    styled_df = pred_df.style.apply(highlight_greaterthan, threshold_val=0.8, column=[pred_df.columns[-1]], axis=1)

    return jsonify(styled_df=styled_df.to_html(table_uuid="group_prediction", classes='display'))


# Performance history
@main.route('/performance_history/')
@login_required
def performance_history():
    page_title = "Performance History"
    filters = ['Filter 1', 'Filter 2', 'Filter 3']
    return render_template('main/performance_history.html', page_title=page_title, filters=filters)


# Get individual performance history
@main.route('/individual_performance/<int:student_id>')
@login_required
def individual_performance(student_id):
    # generate dummy data
    df = generate_performance_history(50)

    # student_id should always be valid
    student_id = 2000000 + student_id % 50

    # get data of that student
    student_df = df[df['Matrikel_Nummer'] == student_id]
    # get Major and degree
    major = student_df['Major'].iloc[0]
    degree = student_df['Degree'].iloc[0]
    # group ECTS and sort by Num_Semester
    student_df = student_df.groupby(by=['Num_Semester'], dropna=False).agg({'ECTS': 'sum'}).sort_values(by=['Num_Semester'])
    # reset index to get Num_Semester as column
    student_df = student_df.reset_index()

    # calculate ECTS cummulative based on Num_Semester
    student_df['ECTS'] = student_df['ECTS'].cumsum()

    response = student_df.to_json(orient='records')
    # add major and degree to json response
    response = json.loads(response)
    # add major and degree to json response as separate object
    response = {'data': response, 'major': major, 'degree': degree}
    response = json.dumps(response)

    return jsonify(response)


# Get group performance history
@main.route('/group_performance/<string:group_id>')
@login_required
def group_performance(group_id):
    # generate dummy data
    df = generate_performance_history(100)

    if group_id == 'degree':
        # group by degree
        grouped_df = df.groupby(by=['Num_Semester', 'Degree'], dropna=False).agg({'ECTS': 'mean'})
    if group_id == 'major':
        # group by studies
        grouped_df = df.groupby(by=['Num_Semester', 'major'], dropna=False).agg({'ECTS': 'mean'}).sort_values(
            by=['Num_Semester'])

    # reset index to get Num_Semester and group as column
    grouped_df = grouped_df.reset_index(0).reset_index()

    return jsonify(grouped_df.to_json(orient='records'))


# Risk Analysis
@main.route('/risk_analysis/')
@login_required
def risk_analysis():
    page_title = "Risk Analysis"
    return render_template('main/risk_analysis.html', page_title=page_title)


# Get risk analysis
@main.route('/get_risk_analysis/<string:feature_id>')
@login_required
def get_risk_analysis(feature_id):
    # generate dummy data
    df = generate_risk_analysis(500)

    # only use the feature that is selected as Feature and the Dropout column
    df = df[[feature_id, 'Dropout']]

    # Perform group by and aggregation
    df = df.groupby([feature_id, 'Dropout']).size().unstack(fill_value=0).reset_index()

    labels = df[feature_id].tolist()
    graduates = df['No'].tolist()
    dropouts = df['Yes'].tolist()

    response = {'labels': labels, 'graduate': graduates, 'dropout': dropouts}
    response = json.dumps(response)

    return jsonify(response)


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
    page_title = "Profile"
    return render_template('main/profile.html', page_title = page_title)


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            current_user.save()  # type: ignore
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

        model = Model(  # type: ignore
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
    ml_databases = current_user.ml_databases  # type: ignore
    return render_template(
        'main/manage_ml_databases.html',
        ml_databases=ml_databases
    )
