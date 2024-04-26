import functions_framework
from google.cloud import bigquery
from common_utils.utils import create_logger
from flask import request, jsonify
import os


@functions_framework.http
def trigger_bq(request):
    request_json = request.get_json(silent=True)
    project_id = os.environ["project_id"]
    dataset_name = os.environ["dataset_name"]
    table_name = os.environ["table_name"]
    logger = create_logger()

    if not request_json:
        return jsonify({"error": "Invalid request. No JSON data found."}), 400
    client = bigquery.Client(project=project_id)

    # BigQuery table reference
    table_ref = client.dataset(dataset_name).table(table_name)

    # Prepare data for insertion
    data_to_insert = [request_json] if isinstance(request_json, dict) else request_json

    # Insert the data into BigQuery
    errors = client.insert_rows_json(table_ref, data_to_insert)

    if errors:
        logger.error(f"Error inserting data into BigQuery: {errors}")
        return jsonify({"status": "error", "message": "Failed to insert data into BigQuery."}), 500

    logger.info(f"Data inserted into {project_id}.{dataset_name}.{table_name} successfully.")
    return jsonify({"status": "success", "message": "Data inserted successfully."}), 200








