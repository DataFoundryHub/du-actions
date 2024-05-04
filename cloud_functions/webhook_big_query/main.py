import functions_framework
from google.cloud import bigquery
from common_utils.utils import create_logger
from flask import request, jsonify


@functions_framework.http
def trigger_bq(request):
    """
    Google Cloud Function to insert JSON data into a BigQuery table based on an HTTP request.
    The function handles requests containing JSON data and attempts to insert them into a specified
    BigQuery table. Returns a success or error message with the appropriate HTTP status code.

    Args:
    - request (Flask request): The HTTP request object containing JSON data to be inserted into BigQuery.

    Expected JSON Structure:
    - The JSON data can be a single object or a list of objects.
    - Single JSON object example:
      {
          "key1": "value1",
          "key2": "value2"
      }
    - List of JSON objects example:
      [
          {"key1": "value1", "key2": "value2"},
          {"key1": "value3", "key2": "value4"}
      ]

    Returns:
    - Flask `jsonify` response with the result of the BigQuery insertion.
    - HTTP status 200 with a success message if the insertion is successful.
    - HTTP status 400 if the request does not contain valid JSON data.
    - HTTP status 500 if an error occurs during the BigQuery insertion.

    Notes:
    - Ensure that the Cloud Function has permissions to interact with BigQuery.
    - The function inserts data into a specified BigQuery project, dataset, and table.
    - If there are errors during insertion, they will be returned in the response.
    """
    # Create a logger for tracking information and errors
    logger = create_logger()

    # Retrieve the JSON data from the HTTP request
    request_json = request.get_json(silent=True)  # 'silent=True' to avoid errors if no JSON is found
    logger.info(f"Received request: {request_json}")  # Log the received JSON data

    # Define the BigQuery project, dataset, and table names
    project_id = "du-labs"  # Google Cloud project ID
    dataset_name = "webhook_dataset"  # BigQuery dataset name
    table_name = "webhook"  # BigQuery table name

    # Return an error response if the JSON data is not provided
    if not request_json:
        return jsonify({"error": "Invalid request. No JSON data found."}), 400

    # Create a BigQuery client for interacting with the BigQuery service
    client = bigquery.Client(project=project_id)

    # Reference the desired BigQuery table
    table_ref = client.dataset(dataset_name).table(table_name)

    # Prepare the data for insertion into BigQuery
    # If the JSON data is a dictionary, wrap it in a list; otherwise, use it as-is
    data_to_insert = [request_json] if isinstance(request_json, dict) else request_json

    # Attempt to insert the data into the specified BigQuery table
    errors = client.insert_rows_json(table_ref, data_to_insert)  # Insert data as JSON

    # If there are any errors during insertion, return an error response with details
    if errors:
        logger.error(f"Error inserting data into BigQuery: {errors}")  # Log the errors
        return jsonify({"status": "error", "message": f"Failed to insert data into BigQuery. Reason - {errors}"}), 500

    # Log a success message if data insertion is successful
    logger.info(f"Data inserted into {project_id}.{dataset_name}.{table_name} successfully.")

    # Return a success response if the data is inserted without errors
    return jsonify({"status": "success", "message": "Data inserted successfully."}), 200  # 200 status for success
