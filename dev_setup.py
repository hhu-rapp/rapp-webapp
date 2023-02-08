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


if __name__ == '__main__':
    app = create_app('development')

    with app.app_context():
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
