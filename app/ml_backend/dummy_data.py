import random
import pandas as pd


def generate_performance_history(n):
    """
    Generates dummy performance history dataframe.

    Parameters
    ----------
    n : int
        Number of students to be generated.

    Returns
    -------
    df : DataFrame
        DataFrame containing the performance history.

    """

    # Define column names for the DataFrame
    columns = ['Matrikel_Nummer', 'Semester', 'Num_Semester', 'Year', 'Major', 'Degree', 'ECTS']

    # Define lists of possible values for each attribute
    majors = ['Informatik', 'Sozialwissenschaften', 'Wirtschaftswissenschaften', 'Rechtswissenschaften']
    degrees = ['Bachelor', 'Master']
    ects_values = [5, 8, 10]
    semesters = ['WS', 'SS']

    # Define maximum ECTS values and year
    max_bachelor_ects = 180
    max_master_ects = 120
    max_year = 2023

    # Create an empty DataFrame with the defined columns
    df = pd.DataFrame(columns=columns)

    # Generate performance history for each student
    for i in range(n):
        matrikel_nummer = 2000000 + i

        # Determine the total number of semesters the student will study
        # 80% chance of 6-8 semesters, 20% chance of 1-5 semesters
        total_semesters = random.randint(6, 8) if random.random() <= 0.8 else random.randint(2, 5)

        # Calculate the starting year based on the total number of semesters
        year = max_year - total_semesters * 2

        # Randomly select the student's major
        major = random.choice(majors)

        # Determine the student's degree (Bachelor or Master) with a 75% chance of being a Bachelor
        degree = random.choice(degrees) if random.random() > 0.75 else 'Bachelor'

        total_ects = 0

        # Generate performance history for each semester
        for curr_semester in range(total_semesters):
            # Determine the semester type (WS or SS) based on the current semester index
            semester = semesters[curr_semester % 2]

            if degree == 'Bachelor':
                # Randomly determine the number of courses the student takes in this semester (2-6 courses)
                num_courses = random.randint(2, 6)

                for _ in range(num_courses):
                    # Randomly select the ECTS value for each course
                    ects = random.choice(ects_values)
                    total_ects += ects

                    # Check if the total ECTS exceeds the maximum allowed for a Bachelor degree
                    if total_ects > max_bachelor_ects:
                        # If it exceeds, randomly decide if student got the maximum ECTS
                        if random.random() > 0.2:
                            continue
                        else:
                            ects = max_bachelor_ects - total_ects
                            if ects < 0:
                                continue
                            total_ects = max_bachelor_ects

                    # Append the course information to the DataFrame
                    df = pd.concat([df, pd.DataFrame({
                        'Matrikel_Nummer': [matrikel_nummer],
                        'Semester': [semester],
                        'Num_Semester': curr_semester + 1,
                        'Year': [year],
                        'Major': [major],
                        'Degree': [degree],
                        'ECTS': [ects]
                    })], ignore_index=True)

                    if total_ects >= max_bachelor_ects:
                        break
            else:
                # Randomly determine the number of courses the student takes in this semester (3-5 courses)
                num_courses = random.randint(3, 5)

                for _ in range(num_courses):
                    # Randomly select the ECTS value for each course
                    ects = random.choice(ects_values)
                    total_ects += ects

                    # Check if the total ECTS exceeds the maximum allowed for a Master degree
                    if total_ects > max_master_ects:
                        # If it exceeds, randomly decide if student got the maximum ECTS
                        if random.random() > 0.2:
                            continue
                        else:
                            ects = max_master_ects - total_ects
                            if ects < 0:
                                continue
                            total_ects = max_master_ects

                    # Append the course information to the DataFrame
                    df = pd.concat([df, pd.DataFrame({
                        'Matrikel_Nummer': [matrikel_nummer],
                        'Semester': [semester],
                        'Num_Semester': curr_semester + 1,
                        'Year': [year],
                        'Major': [major],
                        'Degree': [degree],
                        'ECTS': [ects]
                    })], ignore_index=True)

                    if total_ects >= max_master_ects:
                        break

            # Increase the year for odd semesters (every two semesters)
            if curr_semester % 2 == 1:
                year += 1

    # Return the generated DataFrame
    return df


def generate_risk_analysis(n):
    # Define the sensitive attributes
    sensitive_attributes = ['Sex', 'Nationality', 'Degree', 'Major']

    # Define lists of possible values for each attribute
    sex = ['Male', 'Female', 'Other']
    nationalities = ['German', 'Non-German']
    degrees = ['Bachelor', 'Master']
    majors = ['Informatik', 'Sozialwissenschaften', 'Wirtschaftswissenschaften', 'Rechtswissenschaften']

    dropout_probabilities = {
        'Male': 0.05,
        'Female': 0.03,
        'Other': 0.1,
        'German': 0.05,
        'Non-German': 0.1,
        'Bachelor': 0.2,
        'Master': 0.05,
        'Informatik': 0.2,
        'Sozialwissenschaften': 0.05,
        'Wirtschaftswissenschaften': 0.15,
        'Rechtswissenschaften': 0.09
    }

    # Generate n random student records
    student_data = []
    for _ in range(n):
        student = {}

        # Generate random sensitive attribute values
        student['Sex'] = random.choice(sex)
        student['Nationality'] = random.choice(nationalities)
        student['Degree'] = random.choice(degrees)
        student['Major'] = random.choice(majors)

        # student['Dropout'] = 'No' if random.random() <= 0.8 else 'Yes'

        # Generate dropout probability by adding the probabilities of the sensitive attribute values
        dropout_probability = 0
        for attr in sensitive_attributes:
            dropout_probability += dropout_probabilities[student[attr]]

        student['Dropout'] = 'No' if random.random() > dropout_probability else 'Yes'

        student_data.append(student)

    student_data = pd.DataFrame(student_data)

    return student_data

