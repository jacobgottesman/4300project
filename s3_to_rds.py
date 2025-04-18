# This is the code for the Lambda that connects our input S3 data to our RDS database

import boto3
import csv
import logging
import os
import tempfile
import pymysql

RDS_HOST = 'rds address'
RDS_PORT = 3306
RDS_USER = 'admin'
RDS_PASSWORD = 'rds password'

DATABASE_NAME = '4300finaldb'
TABLE = 'students'

s3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_db_connection():
    return pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def infer_category(assignment):
    a = assignment.lower()
    if "hw" in a or "homework" in a:
        return "Homework"
    elif "exam" in a or "quiz" in a or "midterm" in a:
        return "Exam"
    elif "project" in a or "final" in a or "practical" in a:
        return "Project"
    else:
        return "Other"

def ensure_database_and_table_exists(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        cursor.execute(f"USE {DATABASE}")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                assignment VARCHAR(255),
                category VARCHAR(255),
                max_points INT,
                points INT,
                percentage FLOAT
            )
        """)

def lambda_handler(event, context):
    
    # pull the bucket name from the event
    bucket = event['Records'][0]['s3']['bucket']['name']

    # get the key for the file uploaded
    key = event['Records'][0]['s3']['object']['key']

    logger.info(f"Triggered by upload of file: {key} in bucket: {bucket}")

            # Download and parse JSON file
    response = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(response['Body'].read().decode('utf-8'))

    name = data['name']
    assignment = data['assignment']
    category = infer_category(assignment)
    max_points = data['max_points']
    points = data['points']
    percentage = points / max_points

    conn = get_db_connection()

    try:
        ensure_database_and_table_exists(conn)

        with conn.cursor() as cursor:
            cursor.execute(f"USE {DATABASE}")
            cursor.execute(f"""
                INSERT INTO {TABLE} (name, assignment, category, max_points, points, percentage)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, assignment, category, max_points, points, percentage))

    finally:
        conn.close()


    return {
        'statusCode': 200,
        'body': f"Processed {key} successfully."
    }
