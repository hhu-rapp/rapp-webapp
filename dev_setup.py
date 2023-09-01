import os
import sys
from glob import glob

from app import db, create_app
from app.models import MLDatabase, Model, Query, User, queried_by


def setup_queries_and_models(uploads: str, db_id: int) -> None:
    targets = [f.path for f in os.scandir(uploads) if f.is_dir()]

    for target in targets:
        model_paths = glob(os.path.join(target, '*.joblib'))
        sql_path = glob(os.path.join(target, '*.sql'))[0]
        description_path = os.path.join(target, 'description.txt')

        # Add query
        with open(sql_path, 'r') as f:
            sql_string = f.read()
        query = Query(name=os.path.relpath(target, uploads), query_string=sql_string)

        # Add description
        with open(description_path, 'r') as f:
            description_text = f.read()
        query.description = description_text

        query.save()
        print(f'{os.path.relpath(target, uploads)} query added at {query.id}')

        # Add query and db to relationship
        db.session.execute(queried_by.insert().values(database_id=db_id, query_id=query.id))
        db.session.commit()

        # Add models
        for model_path in model_paths:
            model_name = os.path.splitext(os.path.basename(model_path))[0].split('_')[-1]
            model = Model(name=model_name, filename=os.path.relpath(model_path, uploads), query_id=query.id)
            model.save()
            print(f'{model_name} model added at {query.id}')

    # Add exams performance query
    # Add module average grade
    for sql in glob(os.path.join(uploads, '*.sql')):
        query_name = os.path.splitext(os.path.basename(sql))[0]
        with open(sql, 'r') as f:
            sql_string = f.read()
        query = Query(name=query_name, query_string=sql_string, is_target=False)
        query.save()

        print(f'{query_name} query added at {query.id}')


if __name__ == '__main__':
    app = create_app('development')

    uploads_path = app.config['UPLOAD_FOLDER']

    # if no database was inputted, use the first one
    if sys.argv[1] is None:
        db_path = glob(os.path.join(uploads_path, '*.db'))[0]
        db_name = os.path.splitext(os.path.basename(db_path))[0]
    else:
        assert os.path.splitext(sys.argv[1])[1] == '.db', 'Database must be a .db file'
        db_path = os.path.join(uploads_path, sys.argv[1])
        db_name = os.path.splitext(sys.argv[1])[0]

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
        
        ml_db = MLDatabase(name=db_name, filename=os.path.relpath(db_path, uploads_path), user_id=user.id)
        ml_db.save()

        setup_queries_and_models(uploads_path, ml_db.id)
