import os
from glob import glob

from app import db, create_app
from app.models import MLDatabase, Model, Query, User, queried_by


def setup_queries_and_models(uploads: str, db_id: int) -> None:
    targets = [f.path for f in os.scandir(uploads) if f.is_dir()]

    for target in targets:
        model_paths = glob(os.path.join(target, '*.joblib'))
        sql_path = glob(os.path.join(target, '*.sql'))[0]

        # Add query
        with open(sql_path, 'r') as f:
            sql_string = f.read()
        query = Query(name=os.path.relpath(target, uploads), query_string=sql_string)
        query.save()

        # Add query and db to relationship
        db.session.execute(queried_by.insert().values(database_id=db_id, query_id=query.id))
        db.session.commit()

        # Add models
        for model_path in model_paths:
            model_name = os.path.splitext(os.path.basename(model_path))[0]
            model = Model(name=model_name, filename=os.path.relpath(model_path, uploads), query_id=query.id)
            model.save()

    # Add exams performance query
    sql_string = """
                SELECT S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Note, SSP.Status, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester, AVG(SSP2.Note) AS Durchschnittsnote
                FROM Student AS S, Student_schreibt_Pruefung AS SSP, Pruefung AS P
                JOIN (
                  SELECT *
                  FROM Student_schreibt_Pruefung
                  WHERE Note IS NOT NULL
                ) AS SSP2 ON SSP.Version = SSP2.Version AND SSP.Nummer = SSP2.Nummer AND SSP.Semesterjahr = SSP2.Semesterjahr AND SSP.Sommersemester = SSP2.Sommersemester
                WHERE S.Pseudonym = var_pseudonym
                AND S.Pseudonym = SSP.Pseudonym
                AND SSP.Version = P.Version
                AND SSP.Nummer = P.Nummer
                AND SSP.Fachsemester = var_faculty_semester
                GROUP BY S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester
                ORDER BY SSP.Fachsemester
                """
    
    query = Query(name='exams_performance', query_string=sql_string)
    query.save()

    print(f'exams_performance query added at {query.id}')

if __name__ == '__main__':
    app = create_app('development')

    with app.app_context():
        # Delete all tables
        db.drop_all()
        # Create the database
        db.create_all()

        # Create Admin User
        user = User(email='admin@admin.com', password='admin', is_admin=True)
        user.save()

        uploads_path = app.config['UPLOAD_FOLDER']

        # Add main database
        db_path = glob(os.path.join(uploads_path, '*.db'))[0]
        db_name = os.path.splitext(os.path.basename(db_path))[0]
        ml_db = MLDatabase(name=db_name, filename=os.path.relpath(db_path, uploads_path), user_id=user.id)
        ml_db.save()

        setup_queries_and_models(uploads_path, ml_db.id)
