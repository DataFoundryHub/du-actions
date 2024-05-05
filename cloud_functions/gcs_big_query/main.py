import functions_framework
from google.cloud import bigquery, storage
from common_utils.utils import create_logger
from flask import request, jsonify
import os
import pandas as pd
import pandas_gbq
from datetime import datetime
import traceback


# Define a Cloud Function to handle HTTP-triggered events
@functions_framework.http
def trigger_bq(request):
    """
    This Google Cloud Function is triggered by an HTTP request, usually from a Google Cloud Storage event. It processes a CSV or Parquet file from a specified Cloud Storage bucket, adds an "insert_timestamp" column with the current UTC time, and uploads the data to a BigQuery table.

    Args:
    - request (Flask request): HTTP request containing a JSON payload with the Cloud Storage bucket and file name to process. Expected structure:
      {
          "bucket": "<Cloud Storage bucket name>",
          "name": "<file name in the bucket>"
      }

    Returns:
    - JSON response with status and message indicating the outcome of the operation, and appropriate HTTP status codes:
      - 200 for success (successful data insertion into BigQuery),
      - 400 for invalid request or unsupported file type,
      - 500 for internal errors during processing or BigQuery insertion.

    Notes:
    - Ensure the Cloud Function has appropriate permissions to interact with BigQuery and Google Cloud Storage.
    - Only CSV and Parquet files are supported.
    """
    # Parse the request JSON data to extract necessary information
    request_json = request.get_json(silent=True)  # 'silent=True' returns None if parsing fails
    project_id = "du-labs"  # Set the Google Cloud project ID
    dataset_name = "webhook_dataset"  # Specify the BigQuery dataset
    table_name = "webhook"  # Specify the BigQuery table name

    # Validate the request format
    if not request_json or 'bucket' not in request_json or 'name' not in request_json:
        # Return a 400 error if the request format is invalid
        return jsonify({"status": "error", "message": "Invalid request format."}), 400

    # Create a logger for tracking events
    logger = create_logger()

    # Get the Cloud Storage bucket and file name from the request
    bucket_name = request_json['bucket']
    file_name = request_json['name']

    # Determine the file extension to identify the file type (CSV or Parquet)
    file_extension = os.path.splitext(file_name)[1].lower()  # Get file extension in lowercase

    try:
        # Read the file based on its extension
        if file_extension == ".csv":
            # Read CSV file into a Pandas DataFrame
            df = pd.read_csv(f"gs://{bucket_name}/{file_name}")  # Read directly from GCS
        elif file_extension == ".parquet":
            # Read Parquet file into a Pandas DataFrame
            df = pd.read_parquet(f"gs://{bucket_name}/{file_name}")  # Read directly from GCS
        elif file_extension == ".json":
            # Read JSON file into a Pandas DataFrame
            df = pd.read_json(f"gs://{bucket_name}/{file_name}")  # Read directly from GCS
        else:
            # If the file type is unsupported, return a 400 error
            return jsonify({"status": "error", "message": "Failed to insert data into BigQuery. Reason - invalid file type."}), 400

        # Add an "insert_timestamp" column with the current UTC time
        current_timestamp = datetime.utcnow()  # Get current UTC time
        df["insert_timestamp"] = current_timestamp  # Append the timestamp to the DataFrame

        # Load the data into BigQuery
        pandas_gbq.to_gbq(
            df,
            destination_table=f"{dataset_name}.{table_name}",  # Specify the destination table
            project_id=project_id,  # Specify the project ID
            if_exists='append'  # Append data if the table exists
        )

    except Exception as error:
        # Log the error and return a 500 response with the error message
        logger.error(f"Error Traceback: {traceback.format_exc()}")  # Log the full traceback
        return jsonify({"status": "error", "message": f"An error occurred: {str(error)}"}), 500

    # If everything went well, return a success response
    return jsonify({"status": "success", "message": "Data inserted into BigQuery successfully."}), 200  # 200 status code for success
