# RAPP Webapp

## Overview
The RAPP (Responsible Academic Performance Prediction) Webapp is an innovative solution designed to transform the way academic institutions understand and interact with student performance data. This tool allows for the loading of student databases alongside carefully selected models developed using the [RAPP Tool](https://github.com/hhu-rapp/rapp-tool). The goal is to provide a comprehensive system for analyzing and predicting student performance, as well as early identification of at-rsik students.

## Target Use Case
The RAPP Webapp is ideally suited for universities and educational institutions seeking to:

- **Predict Academic Outcomes:** Utilize data-driven insights to forecast student performance, allowing for proactive academic planning.
- **Identify At-Risk Students:** Detect students who may struggle academically, enabling early intervention strategies.
- **Support Informed Decision-Making:** Provide educators and administrators with comprehensive data to tailor their teaching and support strategies effectively.
- **Promote Fairness:** Employ ethically aligned models to ensure unbiased analysis across diverse student demographics.

## Core Features
- **Seamless Data Integration:** Effortlessly merges student databases with precision-selected predictive models.
- **User-Centric Design:** Tailored for ease of use by all stakeholders in an academic setting, regardless of technical proficiency.
- **Diverse User Access:** Caters to different roles, including administrators and faculty, with specific functionalities.
- **Insightful Dashboard:**  Offers a detailed overview of student data, performance trends, and risk assessments.
- **Predictive and Historical Analysis:** Enables both future-oriented predictions and retrospective evaluations of student performance.


## Requirements
- Python 3.10 or newer

- [Git LFS](https://git-lfs.com/) installed on your system to correctly clone `uploads/rapp_dummy.db`.
## Getting Started

#### Step 1: Clone the Repository
Make sure you have installed git lfs in your system to correctly clone `uploads/rapp_dummy.db`.

Clone the repository:

```bash
git clone https://github.com/hhu-rapp/rapp-webapp.git
```

Calculate the sha265 checksum of `data/rapp_dummy.db` (UNIX-like systems):
```bash
sha256sum uploads/rapp_dummy.db
```

The checksum of the dummy database `data/rapp_dummy.db` should be: 

```bash
d5aac60436d931174f2b02ea32c87c7d32f442021022380e8af376b3d817ee69
```

#### Step 2: Install Dependencies
Ensure you work on a virtual environment and install the dependencies.
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables
1. Navigate to the root folder of the project.
2. Create a file named `.flaskenv` by running the following command in your terminal:
    ```bash
    touch .flaskenv
    ```
3. Once the file is created, open it and add the following content to `.flaskenv`:
    ```bash
    # .flaskenv
    FLASK_APP=rapp.py
    FLASK_CONFIG='development'
    FLASK_DEBUG=True

    ```

#### Step 4: Populate the Database for Development    
1. Navigate to the project directory in your terminal.

2. Run the following command:
    ```bash
    python dev_setup.py [optional_database_name.db]
    ```

    For more information about the script and its functionality, please refer to the [documentation](../..//blob/main/docs/Dev%20Setup.md).

`optional_database_name.db` is the database of the students' performances. It is located in `uploads/`

3. After running the script, the first admin user will be created with the following credentials:

    - Email: admin@admin.com
    - Password: admin
    - Admin Privileges: Yes

These steps will ensure that your database is populated with the necessary data for development or testing purposes.
    

## Local Usage

1. Start the local server by running the following command in your terminal:

    ```bash
    flask run
    ```
2. Once the server is up and running, you can view the webapp in your preferred web browser. By default, you can access the webapp at the following URL: http://127.0.0.1:5000/.
