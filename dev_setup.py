import os
import sys
from glob import glob

from app import db, create_app
from app.models import MLDatabase, Model, Query, User, queried_by

import configparser
import logging
logging.basicConfig(level=logging.INFO)


def setup_targets(uploads: str, db_id: int) -> None:
    """
    Adds all targets to the database

    The targets are the folders in the uploads folder that contain
    - A .sql file with the query
    - A .joblib file with the model
    - A config.ini file with:
        - A [DEFAULT] section with following keys:
            - label: the name of the target
            - description: a description of the target
            - model: the name of the model
    """

    targets = [f.path for f in os.scandir(uploads) if f.is_dir()]

    for target in targets:
        config_path = os.path.join(target, 'config.ini')
        if not os.path.exists(config_path):
            logging.warning(f'config.ini not found in {target}, folder skipped')
            continue

        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')

        try:
            target_name = config['DEFAULT']['label']
            description = config['DEFAULT'].get('description', '')
        except KeyError as e:
            logging.warning(f'config.ini in {target_name} is missing {e} key, folder skipped')
            continue

        model_paths = glob(os.path.join(target, '*.joblib'))
        sql_path = glob(os.path.join(target, '*.sql'))[0]

        # Add query
        with open(sql_path, 'r') as f:
            sql_string = f.read()
        query = Query(name=target_name, query_string=sql_string, description=description)
        query.save()
        logging.debug(query)

        # Add query and db to relationship
        db.session.execute(queried_by.insert().values(database_id=db_id, query_id=query.id))
        db.session.commit()

        # Add model
        for model_path in model_paths:
            model_name = config['DEFAULT'].get('model', os.path.splitext(os.path.basename(model_path))[0])
            model = Model(name=model_name, filename=os.path.relpath(model_path, uploads), query_id=query.id)
            model.save()
            logging.debug(model)

        logging.info(f'{target_name} target added')


def setup_functional_queries(uploads: str) -> None:
    """
    Adds all functional queries to the database
    Functional queries are .sql files in the uploads folder
    """
    # Add exams performance query
    # Add module average grade
    for sql in glob(os.path.join(uploads, '*.sql')):
        query_name = os.path.splitext(os.path.basename(sql))[0]
        with open(sql, 'r') as f:
            sql_string = f.read()
        query = Query(name=query_name, query_string=sql_string, is_target=False)
        query.save()

        logging.debug(query)


if __name__ == '__main__':
    app = create_app('development')

    uploads_path = app.config['UPLOAD_FOLDER']
    database_path = app.config['SQLALCHEMY_DATABASE_URI']

    # if no database was inputted, use rapp_dummy.db
    if len(sys.argv) <= 1:
        db_path = os.path.join(uploads_path, 'rapp_dummy.db')
        db_name = 'rapp_dummy'
    else:
        assert os.path.splitext(sys.argv[1])[1] == '.db', 'Database must be a .db file'

        db_path = os.path.join(uploads_path, sys.argv[1])
        db_name = os.path.splitext(sys.argv[1])[0]

        if not os.path.exists(db_path):
            raise FileNotFoundError(f'{db_path} does not exist in {uploads_path}')

    logging.info(f'Using {db_path} as database')

    with app.app_context():
        db.drop_all()
        # Create the database
        db.create_all()

        # Create Admin User
        user = User(email='admin@admin.com', password='admin', is_admin=True)
        user.save()

        # Add main database
        ml_db = MLDatabase(name=db_name, filename=os.path.relpath(db_path, uploads_path), user_id=user.id)
        ml_db.save()

        # setup_queries_and_models(uploads_path, ml_db.id)
        setup_targets(uploads_path, ml_db.id)
        setup_functional_queries(uploads_path)

        logging.info('Database setup complete')
