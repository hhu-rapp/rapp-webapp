# rapp-user-frontend

## Requirements
Python>=3.10

## Installation
1. Clone the repo

    Please choose one of following:

    - Clone with SSH:
        ```bash
        git clone git@gitlab.cs.uni-duesseldorf.de:dbs/research/project/rapp/rapp-user-frontend.git
        ```

    - Clone with https:
        ```bash
        git clone https://gitlab.cs.uni-duesseldorf.de/dbs/research/project/rapp/rapp-user-frontend.git
        ```
2. Create a virtual environment
    ```bash
    cd rapp-user-frontend
    python -m venv .venv
    ```
3. Activate virtual environment

    On windows use:
    ```
    .venv\Scripts\activate.bat
    ```

    On Mac/Unix use:
    ```bash
    source .venv/bin/activate
    ```
4. Install python dependencies
    ```
    pip install -r requirements.txt
    ```
5. Create .flaskenv file
    
    For the following commands to work (and easier development) the use of an environment file is neccessary. 

    Create a file named ".flaskenv" within the root folder of this project:
    ```bash
    touch .flaskenv
    ```
    with the following content:
    ```
    # .flaskenv
    FLASK_APP=rapp.py
    FLASK_CONFIG='development'
    FLASK_DEBUG=True
    ```
    (The file should be in the same folder this README.md file is in.)
    
6. Initialize database (development only):

    To populate the database with essential data for development purposes, follow these steps:


    1. Navigate to the project directory.

    2. Run the following command:

        ```bash
        python dev_setup.py
        ```

        This script will initialize the database with initial data required for development.


        - To load a custom database, add the argument database.db with the name of your database file, including the .db extension.

        - Ensure that the .db file is located in the uploads/ directory before running the command.

        This command enables dynamic selection of the database. If you don't provide a specific database filename, the script will use the first .db file found in the uploads/ directory by default.

    3. After running the script, the first admin user will be created with the following credentials:

    - Email: admin@admin.com
    - Password: admin
    - Admin Privileges: Yes
    

## Usage

1. Start local server (development only)

    ```bash
    flask run
    ```
2. View website in preferred browser

    With default settings the website can be found at http://127.0.0.1:5000/.
