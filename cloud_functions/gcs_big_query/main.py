import functions_framework
from google.cloud import bigquery, storage
from common_utils.utils import create_logger
from flask import request, jsonify
import os
import pandas as pd
from io import StringIO


@functions_framework.http
def trigger_bq(request):
    request_json = request.get_json(silent=True)
    project_id = "du-labs"
    dataset_name = "webhook_dataset"
    table_name = "webhook"
    logger = create_logger()
    bucket_name = request_json['bucket']
    file_name = request_json['name']

    # Determine the file type (CSV or Parquet)
    file_extension = os.path.splitext(file_name)[1].lower()

    # BigQuery client
    client = bigquery.Client(project=project_id)

    # Google Cloud Storage client
    gcs_client = storage.Client()

    # Fetch the file from GCS
    bucket = gcs_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    if file_extension == ".csv":
        # Read CSV file into a DataFrame
        #csv_data = blob.download_as_bytes()  # Download the CSV content as bytes
        df = pd.read_csv(f"{bucket_name}/{file_name}")
    elif file_extension == ".parquet":
        # Read Parquet file into a DataFrame
        #with blob.open("rb") as f:
        df = pd.read_parquet(f"{bucket_name}/{file_name}")
    else:
        # Unsupported file type
        return jsonify({"status": "error", "message": "Failed to insert data into BigQuery. Reason - invalid file type."}), 500

    # Load DataFrame into BigQuery
    df.to_gbq(destination_table=f"{dataset_name}.{table_name}",
              project_id=project_id,
              if_exists='append')
