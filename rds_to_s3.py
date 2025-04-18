# this is the code for the lambda that connects our RDS back to the S3 bucket with final processed data 

import pymysql
import boto3
import csv
import io
import logging
from collections import defaultdict

RDS_HOST = 'rds address'
RDS_PORT = 3306
RDS_USER = 'admin'
RDS_PASSWORD = 'rds password'

DATABASE = '4300finaldb'
TABLE ='students'

# S3 config
OUTPUT_BUCKET_NAME = '4300-final-project'
OUTPUT_KEY = 'results/grades_summary.csv'

# Clients
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

def lambda_handler(event, context):
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"USE {DATABASE}")
            cursor.execute(f"SELECT name, category, max_points, points FROM {TABLE}")
            rows = cursor.fetchall()
    finally:
        conn.close()
    
    # Aggregate scores
    students = defaultdict(lambda: defaultdict(lambda: {'points': 0, 'max_points': 0}))

    for row in rows:
        name = row['name']
        category = row['category']
        students[name][category]['points'] += row['points']
        students[name][category]['max_points'] += row['max_points']
        students[name]['Total']['points'] += row['points']
        students[name]['Total']['max_points'] += row['max_points']
    
    categories = ['Homework', 'Exam', 'Project', 'Other']
    headers = ['name'] + categories + ['Total']

    # Write to CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for student, cat_scores in students.items():
        row = [student]
        for cat in categories:
            if cat in cat_scores:
                score = (cat_scores[cat]['points'] / cat_scores[cat]['max_points']) * 100
                row.append(round(score, 2))
            else:
                row.append('')
        total = (cat_scores['Total']['points'] / cat_scores['Total']['max_points']) * 100
        row.append(round(total, 2))
        writer.writerow(row)

    # Upload CSV to S3
    s3.put_object(
        Bucket=OUTPUT_BUCKET_NAME,
        Key=OUTPUT_KEY,
        Body=output.getvalue().encode('utf-8'),
        ContentType='text/csv'
    )

    logger.info(f"Exported CSV to s3://{OUTPUT_BUCKET_NAME}/{OUTPUT_KEY}")

    return {
        'statusCode': 200,
        'body': f"Exported CSV to s3://{OUTPUT_BUCKET_NAME}/{OUTPUT_KEY}"
    }

