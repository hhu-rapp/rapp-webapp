import numpy as np

import json

import pandas as pd
from flask import render_template, jsonify, abort
from flask_login import login_required

from scipy import stats

from . import main
from ..ml_backend import query_database
from ..ml_backend.dummy_data import generate_risk_analysis
from ..models import Query, MLDatabase


# Performance history
@main.route('/performance_history/')
@login_required
def performance_history():
    page_title = "Performance History"
    majors = ['Informatik', 'Sozialwissenschaften', 'all']
    return render_template('main/performance_history.html', page_title=page_title, majors=majors)


# Get individual performance history
@main.route('/individual_performance/<int:student_id>')
@login_required
def individual_performance(student_id):
    # FIXME: Hardcoded Database replace with db_id from session_id
    db = MLDatabase.query.get_or_404(1)
    # FIXME: Hardcoded functional query name
    query_name = "performance_history"
    query_string = Query.query.filter_by(name=query_name).first_or_404()
    performance_df = query_database(db, query_string)

    df = performance_df

    # Get the Major and degree of the specific student
    student = df.loc[df['Pseudonym'] == student_id]
    if student.empty:
        abort(404)

    major = student['Studienfach'].iloc[0]
    degree = student['Abschluss'].iloc[0]

    # Filter to include only students with the same major and degree
    degree_major_students_df = df.loc[(df['Studienfach'] == major) & (df['Abschluss'] == degree)]
    # Calculate the number of unique students
    n_students = len(degree_major_students_df['Pseudonym'].unique())

    # Sum the ECTS gathered by each student per semester
    all_students_grouped = degree_major_students_df.groupby(by=['Fachsemester', 'Pseudonym'], dropna=False).agg(
        {'ECTS': 'sum'}).sort_values(
        by=['Fachsemester', 'Pseudonym'])

    # Reset the level of index to convert it into a column
    all_student_ects_df = all_students_grouped.reset_index(level=1)

    # Calculate cumulative ECTS for each student
    all_student_ects_df['ECTS'] = all_student_ects_df.groupby('Pseudonym')['ECTS'].cumsum()

    # Create a continuous range of 'Fachsemester' values
    student_df = all_student_ects_df[all_student_ects_df['Pseudonym'] == student_id].reset_index()
    # Create a continuous range of 'Fachsemester' values
    continuous_fachsemester = pd.DataFrame({'Fachsemester': range(1, student_df['Fachsemester'].max() + 1)})
    # Merge the continuous range with the student's ECTS points
    student_ects = pd.merge(continuous_fachsemester, student_df, on='Fachsemester', how='left')['ECTS']
    # Fill NaN values with previous ECTS points
    student_ects = student_ects.fillna(method='ffill')

    # Calculate the average ECTS points for each semester across all students
    average_ects = all_student_ects_df.groupby('Fachsemester')['ECTS'].mean().round(1)

    # Calculate the standard error of the mean for each semester
    sem_ects = all_student_ects_df.groupby('Fachsemester')['ECTS'].sem()

    # Filter out semesters with NaN SEM values
    valid_sem_ects = np.isfinite(sem_ects)
    valid_average_ects = average_ects[valid_sem_ects]
    valid_sem_ects = sem_ects[valid_sem_ects]

    # Calculate the confidence interval for the average ECTS points
    lower_bound, upper_bound = stats.t.interval(0.95, df=n_students - 1, loc=valid_average_ects, scale=valid_sem_ects)
    response = {
        'single_student': student_ects.to_list(),
        'all_students': json.loads(average_ects.reset_index().to_json(orient='records')),
        'lower_int': list(np.around(np.array(lower_bound), 1)),
        'upper_int': list(np.around(np.array(upper_bound), 1)),
        'major': major,
        'degree': degree
    }
    response = json.dumps(response)

    return jsonify(response)


# Get group performance history
@main.route('/group_performance/<string:major_id>/<string:degree_id>')
@login_required
def group_performance(major_id, degree_id):
    # FIXME: Hardcoded Database replace with db_id from session_id
    db = MLDatabase.query.get_or_404(1)
    # FIXME: Hardcoded functional query name
    query_name = "performance_history"
    query_string = Query.query.filter_by(name=query_name).first_or_404()
    df = query_database(db, query_string)

    # Drop rows with no passed exams
    df = df[df['ECTS'] > 0]

    # filter by major and degree
    if not major_id == 'all':
        df = df.loc[df['Studienfach'] == major_id]

    if not degree_id == 'all':
        df = df.loc[df['Abschluss'] == degree_id]

    if df.empty:
        abort(404)

    # group by degree
    grouped_df = df.groupby(by=['Fachsemester', 'Abschluss'], dropna=False).agg({'ECTS': 'mean'}).round(1)

    # reset index to get Num_Semester and group as column
    grouped_df = grouped_df.reset_index(0).reset_index()

    return jsonify(grouped_df.to_json(orient='records'))


# Risk Analysis
@main.route('/risk_analysis/')
@login_required
def risk_analysis():
    page_title = "Risk Analysis"
    majors = ['Informatik', 'Sozialwissenschaften', 'Wirtschaftswissenschaften', 'Rechtswissenschaften', 'all']
    return render_template('main/risk_analysis.html', page_title=page_title, majors=majors)


# Get risk analysis
@main.route('/get_risk_analysis/<string:major_id>/<string:degree_id>/<string:demographics_id>')
@login_required
def get_risk_analysis(major_id, degree_id, demographics_id):
    # generate dummy data
    df = generate_risk_analysis(500)

    # filter by major and degree
    if not major_id == 'all':
        df = df.loc[df['Major'] == major_id]

    if not degree_id == 'all':
        df = df.loc[df['Degree'] == degree_id]

    # only use the feature that is selected as Feature and the Dropout column
    df = df[[demographics_id, 'Dropout']]

    # Perform group by and aggregation
    df = df.groupby([demographics_id, 'Dropout']).size().unstack(fill_value=0).reset_index()

    labels = df[demographics_id].tolist()
    graduates = df['No'].tolist()
    dropouts = df['Yes'].tolist()

    response = {'labels': labels, 'graduate': graduates, 'dropout': dropouts}
    response = json.dumps(response)

    return jsonify(response)
