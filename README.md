# 4300project

## Files

### `app.py`

This is our main file and has ll our code for running both the input and output end of our project. You can run it locally typing `streamlit run app.py` in terminal. 

### `src/s3_uploader.py`

This is a modified version of the provided code for connecting S3 to python. We added functions for sending JSON data to S3.

### `s3_to_rds.py` and `rds_to_s3.py`

These files contain the code used in our lambdas. First, the fie s3 to rds code is used to get the data that we upload as jsons into one RDS database table. That triggers the rds to s3 lambada which takes the mostly unprocessed rds data and aggregates it by student into a new grade summary table in S3, which is ingested by the streamlit grade viewer.