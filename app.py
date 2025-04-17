import streamlit as st
from src.s3_uploader import *
import pandas as pd
import os


def get_students():
# get all students

    with open('students.txt', 'rb') as f:
        students = f.readlines()
    
    return [name.decode('utf-8').strip() for name in students]

def add_student(student):
# add new student

    with open('students.txt', 'a') as f:
        f.write(student + '\n')


def get_assignments():
# get all assignments

    with open('assignments.txt', 'rb') as f:
        assignments = f.readlines()
    
    return [name.decode('utf-8').strip() for name in assignments]

def add_assignment(assignment):
# add a new assignment

    with open('assignments.txt', 'a') as f:
        f.write(assignment + '\n')




def create_streamlit_app(client, bucket):
    # Page layout
    st.set_page_config(page_title="Grading Tool")

    # Header
    st.title("4300 Final Project Grading Tool")
    st.markdown("By Jacob Gottesman and Marcos Esquiza Gasco")

    # Sidebar
    with st.sidebar:
        page = st.radio(
            "Choose a Page to View",
            ("Grade Entry Tool", "Grade Viewer")
        )

    # load grade entry ool if selected
    if page == "Grade Entry Tool":
        input_tool(client, bucket)
    



def input_tool(client, bucket):

    # add student input section
    students = get_students()
    name = st.selectbox("Select Student", students)
    if name == "Other":
        new_name = st.text_input("Student Name:", max_chars = 50)
        if new_name:
            add_student(new_name)
            name = new_name
            students = get_students()

    # add assignment input section
    assignments = get_assignments()
    assignment = st.selectbox("Select Assignment", assignments)
    if assignment == "Other":
        new_assignment = st.text_input("Assignment Name:", max_chars = 50)
        if new_assignment:
            add_assignment(new_assignment)
            assignment = new_assignment
            assignments = get_assignments()

    # max point and student score
    assignment_max_points = st.number_input("Max Assignment Points", min_value = 0, value = 100)
    score = st.number_input("Score", min_value = 0, max_value = assignment_max_points)

    # submit button
    submit = st.button("Submit Grade")

    # get in proper json format and upload to S3
    if submit:
        if name and assignment and assignment_max_points and score:
            to_db = {'name': name, 'assignment': assignment, 
                    'max_points': assignment_max_points, 'points': score}
            
            upload_dict_as_json_to_s3(client, to_db, bucket, f'{name.replace(' ', '_')}_{assignment.replace(' ', '_')}.json')



def main():
    # Load AWS credentials from .env
    aws_credentials = load_env_variables()

    # Validate required environment variables
    if not aws_credentials["aws_access_key_id"]:
        raise ValueError("No AWS Access key id set")
    if not aws_credentials["aws_secret_access_key"]:
        raise ValueError("No AWS Secret Access key set")
    if not aws_credentials["aws_region"]:
        raise ValueError("No AWS Region Set")
    if not aws_credentials["s3_bucket_name"]:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")

    # Using the boto3 library, initialize S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name=aws_credentials["aws_region"],
    )
    

    create_streamlit_app(s3_client, aws_credentials['s3_bucket_name'])


if __name__ == "__main__":
    main()