# rapp-user-frontend

## Installation
1. Clone the repo

    Please choose one of following:

    - Clone with SSH:
        ```
        git clone git@gitlab.cs.uni-duesseldorf.de:dbs/research/project/rapp/rapp-user-frontend.git
        ```

    - Clone with https:
        ```
        git clone https://gitlab.cs.uni-duesseldorf.de/dbs/research/project/rapp/rapp-user-frontend.git
        ```
2. Create a virtual environment
    ```
    cd rapp-user-frontend
    python -m venv .venv
    ```
3. Activate virtual environment

    On windows use:
    ```
    .venv\Scripts\activate.bat
    ```

    On Mac/Unix use:
    ```
    source .venv/bin/activate
    ```
4. Install python dependencies
    ```
    pip install -r requirements.txt
    ```
5. Create .flaskenv file
    ```
    touch .flaskenv
    ```
    For the following commands to work (and easier development) the use of an environment file is neccessary. 

    Create a file named ".flaskenv" within the root folder of this project with the following content:
    ```
    # .flaskenv
    FLASK_APP=rapp.py
    FLASK_CONFIG='development'
    FLASK_DEBUG=True
    ```
    (The file should be in the same folder this README.md file is in.)
    
6. Initialize database

    Open flask shell:
    ```
    flask shell
    ```

    Within the shell execute the following commands to initialize the database:
    ```
    db.create_all()
    ```

7. Create first admin (development only):
    While still in Flask Shell, run

    ```
    user = User(email='admin@admin.com', password='admin', is_admin=True)
    db.session.add(user)
    db.session.commit()
    ```

    To exit the shell use:
    ```
    exit()
    ```

    Email and password can be chosen arbitrarily.

## Usage
1. Start local server (development only)

    ```
    flask run
    ```
2. View website in preferred browser

    With default settings the website can be found at http://127.0.0.1:5000/.
