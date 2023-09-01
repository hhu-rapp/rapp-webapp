import numpy as np
import json

from flask import render_template, jsonify, abort
from flask_login import current_user, login_required

from . import main
from ..ml_backend import query_database
from ..ml_backend.dummy_data import generate_performance_history, generate_risk_analysis
from ..models import News, Query, MLDatabase

from . import views_predictions, views_admin, views_historical_data, views_account


@main.route('/')
@login_required
def index():
    page_title = "Dashboard"
    news: News = News.query.order_by(News.timestamp.desc()).all()

    notifications = [{"link": '/prediction/1/1/1', "title": 'New Prediction', "mins_ago": 10},
                     {"link": '/performance_history', "title": 'New Performance History', "mins_ago": 15}]
    majors = ['Informatik', 'Sozialwissenschaften', 'all']
    return render_template('main/dashboard.html', news=news, notifications=notifications, page_title=page_title,
                           majors=majors)


# Ajax call for the dashboard
@main.route('/dashboard-data/<string:major_id>/<string:degree_id>')
@login_required
def dashboard_data(major_id, degree_id):
    db_id = 1
    db = MLDatabase.query.get_or_404(db_id)
    query_name = "performance_history"
    query_string = Query.query.filter_by(name=query_name).first_or_404()
    performance_df = query_database(db, query_string)

    # get total number of students
    query_string = """
        Select E.Pseudonym, E.Abschluss, E.Studienfach
        FROM Einschreibung E
        Where Exmatrikulationsdatum is ''
        """
    registered_students_df = query_database(db, query_string)

    avg_bachelor_semesters = '-'
    avg_master_semesters = '-'

    if major_id != 'all':
        performance_df = performance_df[performance_df['Studienfach'] == major_id]
        registered_students_df = registered_students_df[registered_students_df['Studienfach'] == major_id]

    if degree_id == 'bachelor':
        performance_df = performance_df[performance_df['Abschluss'] == 'Bachelor']
        registered_students_df = registered_students_df[registered_students_df['Abschluss'] == 'Bachelor']

    elif degree_id == 'master':
        performance_df = performance_df[performance_df['Abschluss'] == 'Master']
        registered_students_df = registered_students_df[registered_students_df['Abschluss'] == 'Master']

    if performance_df.empty or registered_students_df.empty:
        abort(404)

    total_students = registered_students_df['Pseudonym'].nunique()

    # avg number of semesters for all students
    # group by student id and get sum of ECTS, max number of semesters and degree
    group_performance = performance_df.groupby('Pseudonym').agg(
        {'ECTS': 'sum', 'Fachsemester': 'max', 'Abschluss': 'max'}).reset_index()

    if degree_id != 'master':
        # get students that have 180 ECTS and are in bachelor
        bachelor_students = group_performance[
            (group_performance['ECTS'] >= 180) & (group_performance['Abschluss'] == 'Bachelor')]
        # get avg number of semesters for bachelor students
        avg_bachelor_semesters = round(bachelor_students['Fachsemester'].mean(), 0)

        if np.isnan(avg_bachelor_semesters):
            avg_bachelor_semesters = 6

    if degree_id != 'bachelor':
        # get students that have 120 ECTS and are in master
        master_students = group_performance[
            (group_performance['ECTS'] >= 120) & (group_performance['Abschluss'] == 'Master')]
        # get avg number of semesters for master students
        avg_master_semesters = round(master_students['Fachsemester'].mean(), 0)

        if np.isnan(avg_master_semesters):
            avg_master_semesters = 4

    # avg ects per semester
    group_performance = performance_df.groupby(['Pseudonym', 'Sommersemester', 'Semesterjahr']).agg(
        {'ECTS': 'sum'}).reset_index()
    avg_ects_per_semester = round(group_performance['ECTS'].mean(), 0)

    # get data for plots get only unique Matrikel_Nummer
    group_performance = performance_df.groupby('Pseudonym').agg(
        {'Geschlecht': 'max', 'Deutsch': 'max'}).reset_index()

    sex_plot = group_performance['Geschlecht'].value_counts().reset_index().sort_values(by='Geschlecht',
                                                                                        ascending=False).rename(
        columns={'index': 'labels', 'Geschlecht': 'data'})

    # replace binary labels with actual values
    group_performance['Deutsch'] = group_performance['Deutsch'].replace(
        {0: 'Nicht-Deutsch', 1: 'Deutsch'})

    nat_plot = group_performance['Deutsch'].value_counts().reset_index().sort_values(by='Deutsch',
                                                                                     ascending=False).rename(
        columns={'index': 'labels', 'Deutsch': 'data'})

    # add all values to response
    response = {'totalStudents': total_students,
                'avgBachelorSemesters': avg_bachelor_semesters,
                'avgMasterSemesters': avg_master_semesters,
                'avgEctsPerSemester': avg_ects_per_semester,
                'sexPlot': json.dumps(sex_plot.to_dict('list')),
                'natPlot': json.dumps(nat_plot.to_dict('list'))}

    response = json.dumps(response, default=str)

    return jsonify(response)


@main.route('/home')
@login_required
def home():
    ml_databases = current_user.ml_databases  # type: ignore
    return render_template(
        'main/home.html',
        ml_databases=ml_databases
    )
