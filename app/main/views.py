import numpy as np
import json

from flask import render_template, jsonify
from flask_login import current_user, login_required

from . import main
from ..ml_backend.dummy_data import generate_performance_history, generate_risk_analysis
from ..models import News

from . import views_predictions, views_admin, views_historical_data, views_account


@main.route('/')
@login_required
def index():
    page_title = "Dashboard"
    news: News = News.query.order_by(News.timestamp.desc()).all()

    notifications = [{"link": '/prediction/1/1/1', "title": 'New Prediction', "mins_ago": 10},
                     {"link": '/performance_history', "title": 'New Performance History', "mins_ago": 15}]
    majors = ['Informatik', 'Sozialwissenschaften', 'Wirtschaftswissenschaften', 'Rechtswissenschaften', 'all']
    return render_template('main/dashboard.html', news=news, notifications=notifications, page_title=page_title,
                           majors=majors)


# Ajax call for the dashboard
@main.route('/dashboard-data/<string:major_id>/<string:degree_id>')
@login_required
def dashboard_data(major_id, degree_id):
    # generate dummy performance data
    performance_df = generate_performance_history(100)
    # generate dummy risk analysis data
    dropout_df = generate_risk_analysis(100)

    avg_bachelor_semesters = '-'
    avg_master_semesters = '-'

    if major_id == 'all':
        performance_df = performance_df
        dropout_df = dropout_df
    else:
        performance_df = performance_df[performance_df['Major'] == major_id]
        dropout_df = dropout_df[dropout_df['Major'] == major_id]

    if degree_id == 'bachelor':
        performance_df = performance_df[performance_df['Degree'] == 'Bachelor']
        dropout_df = dropout_df[dropout_df['Degree'] == 'Bachelor']

    elif degree_id == 'master':
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

    if degree_id != 'master':
        # get students that have 180 ECTS and are in bachelor
        bachelor_students = group_performance[
            (group_performance['ECTS'] >= 180) & (group_performance['Degree'] == 'Bachelor')]
        # get avg number of semesters for bachelor students
        avg_bachelor_semesters = round(bachelor_students['Num_Semester'].mean(), 0)

        if np.isnan(avg_bachelor_semesters):
            avg_bachelor_semesters = 6

    if degree_id != 'bachelor':
        # get students that have 120 ECTS and are in master
        master_students = group_performance[
            (group_performance['ECTS'] >= 120) & (group_performance['Degree'] == 'Master')]
        # get avg number of semesters for master students
        avg_master_semesters = round(master_students['Num_Semester'].mean(), 0)

        if np.isnan(avg_master_semesters):
            avg_master_semesters = 4

    # avg ects per semester
    group_performance = performance_df.groupby(['Matrikel_Nummer', 'Semester', 'Year']).agg(
        {'ECTS': 'sum'}).reset_index()
    avg_ects_per_semester = round(group_performance['ECTS'].mean(), 0)

    # get data for plots get only unique Matrikel_Nummer
    group_performance = performance_df.groupby('Matrikel_Nummer').agg(
        {'Sex': 'max', 'Nationality': 'max'}).reset_index()

    sex_plot = group_performance['Sex'].value_counts().reset_index().sort_values(by='Sex', ascending=False).rename(
        columns={'index': 'labels', 'Sex': 'data'})

    nat_plot = group_performance['Nationality'].value_counts().reset_index().sort_values(by='Nationality',
                                                                                         ascending=False).rename(
        columns={'index': 'labels', 'Nationality': 'data'})

    # add all values to response
    response = {'totalStudents': total_students,
                'totalDropouts': total_dropouts,
                'avgBachelorSemesters': avg_bachelor_semesters,
                'avgMasterSemesters': avg_master_semesters,
                'avgEctsPerSemester': avg_ects_per_semester,
                'sexPlot': json.dumps(sex_plot.to_dict('list')),
                'natPlot': json.dumps(nat_plot.to_dict('list'))}

    response = json.dumps(response)

    return jsonify(response)


@main.route('/home')
@login_required
def home():
    ml_databases = current_user.ml_databases  # type: ignore
    return render_template(
        'main/home.html',
        ml_databases=ml_databases
    )
