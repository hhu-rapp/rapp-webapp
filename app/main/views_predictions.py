import pandas as pd
import sqlalchemy
from joblib import load

from flask import abort, current_app, render_template, request, jsonify
from flask_login import current_user, login_required

from . import main
from ..models import MLDatabase, Model, News, Query, User
from ..ml_backend import pipeline, highlight_greaterthan, query_database


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
    # Placeholder for session id
    session_id = 1

    db = MLDatabase.query.get_or_404(db_id)
    query = Query.query.get_or_404(query_id)
    model = Model.query.get_or_404(model_id)

    if db.user_id != current_user.id or not current_user.is_admin:
        abort(403)

    df = query_database(db, query).drop(['Pseudonym'], axis=1)
    label = query.name

    estimator = load(current_app.config['UPLOAD_FOLDER'] + '/' + model.filename)['model']
    pred_df = pipeline.predict(estimator, df, label)

    df.insert(0, ' ', df.apply(lambda row: f'<a class="btn bg-gradient-secondary" '
                                                     f'href="/student-review/{session_id}/{row.name}">Review</a>',
                                         axis=1))

    # Drop sensitive attributes, Geschlecht, Deutsch and AlterEinschreibung
    df = df.drop(['Geschlecht', 'Deutsch', 'AlterEinschreibung'], axis=1)

    styled_df = df.style.apply(highlight_greaterthan, threshold_val=0.8, column=[pred_df.columns[-1]], axis=1)
    styled_df.format(precision=1)

    return render_template('main/machine-learning.html', styled_df=styled_df, features=pred_df.columns[:-1],
                           page_title=page_title)


@main.route('/student-review/<int:session_id>/<int:row_id>')
@login_required
def student_review(session_id, row_id):
    page_title = f"Student {row_id}"

    # FIXME: Hardcoded Database replace with db_id from session_id
    db = MLDatabase.query.get_or_404(session_id)
    # FIXME: Hardcoded Query replace with query_id from session_id
    query = Query.query.get_or_404(session_id)

    pseudonym = query_database(db, query).iloc[row_id, 0]

    # Add query for fachsemester
    query = f"""
    SELECT S.Pseudonym, MAX(SSP.Fachsemester) as Fachsemester, E.Studienfach, E.Abschluss
    FROM
      Student as S,
      Student_schreibt_Pruefung as SSP,
      Einschreibung as E
    WHERE
        S.Pseudonym = SSP.Pseudonym
    AND E.Pseudonym = SSP.Pseudonym
    AND S.Pseudonym = {pseudonym}
    """

    student_data = query_database(db, query).to_dict(orient='records')[0]

    # Get total ECTS
    query = f"""
    SELECT SUM(SSP.ECTS) AS total_ects
    FROM Student_schreibt_Pruefung AS SSP
    WHERE SSP.Pseudonym = {pseudonym}
    GROUP BY SSP.Pseudonym;
    """

    total_ects = query_database(db, query).iloc[0, 0]

    # Get Year and Semester of first exam
    query = f"""
    SELECT Pseudonym, Semesterjahr, Sommersemester
    FROM Student_schreibt_Pruefung
    WHERE Pseudonym = {pseudonym}
    ORDER BY Semesterjahr ASC, Sommersemester DESC
    LIMIT 1;
    """

    first_exam = query_database(db, query).to_dict(orient='records')[0]

    return render_template('main/student-review.html', page_title=page_title, pseudonym=pseudonym,
                           session_id=session_id, student_data=student_data,
                           total_ects=total_ects, first_exam=first_exam)


@main.route('/get-semester-data/<int:session_id>/<int:pseudonym>/<int:semester_id>')
@login_required
def student_semester_data(session_id, pseudonym, semester_id):
    # FIXME: Hardcoded Database replace with db_id from session_id
    db = MLDatabase.query.get_or_404(session_id)
    # FIXME: Hardcoded Query replace with query_id for exams_performance from session_id
    query_string = Query.query.get_or_404(2)

    # Get semester data
    bindparams = {'pseudonym': str(pseudonym), 'semester': str(semester_id)}
    semester_data = query_database(db, query_string, bindparams=bindparams)

    def get_modul_average(modul):
        query_string = Query.query.get_or_404(3)
        semester_data = query_database(db, query_string, bindparams={'module': str(modul)})
        # print(semester_data)
        return semester_data['Durchschnittsnote'][0]

    if semester_data.empty:
        return jsonify([])
    # concat Durchschnittsnote and Standardabweichung and add ± in between
    semester_data['Durchschnittsnote'] = semester_data['Durchschnittsnote'].round(2).astype(str) + ' ± 0.1'

    # add new column ModulDurchschnitt only if 
    semester_data['ModulDurchschnitt'] = semester_data['Modul'].apply(lambda modul: get_modul_average(modul))
    semester_data['ModulDurchschnitt'] = semester_data['ModulDurchschnitt'].round(2).astype(str) + ' ± 0.2'

    # fill missing values with '-'
    semester_data = semester_data.fillna('-')

    return jsonify(semester_data.to_dict(orient='records'))


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

    df = query_database(db, query).drop(['Pseudonym'], axis=1)
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
    styled_df.format(precision=1)

    return jsonify(styled_df=styled_df.to_html(table_uuid="group_prediction", table_attributes='class="w-100"'))
