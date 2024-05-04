import functions_framework
from google.cloud import bigquery
from common_utils.utils import create_logger
from big_query_ops import BigQueryDDL


# Define a Cloud Function that handles HTTP requests to trigger BigQuery operations
@functions_framework.http
def trigger_bq(request):
    """
    Google Cloud Function to perform BigQuery Data Definition Language (DDL) operations based on HTTP request data.
    The function can create, update, or delete BigQuery tables based on the 'operation' specified in the request JSON.

    Args:
    - request (Flask request): The HTTP request object. Expected to contain JSON data with necessary information for
      performing BigQuery operations, including:
      - "project_id": Google Cloud project ID.
      - "dataset_name": Name of the BigQuery dataset.
      - "dataset_location": Location of the dataset (e.g., 'US', 'EU').
      - "table_name": Name of the BigQuery table.
      - "operation": The type of DDL operation to perform ('CREATE', 'UPDATE', 'DELETE').
      - "schema": Schema information (required for CREATE and UPDATE operations, optional for DELETE).

    Returns:
    - A dictionary with a 'status' key indicating 'success' or 'error', and a 'message' key describing the outcome.
    - If there's an error, the response may contain an error message and a relevant HTTP status code.

    Notes:
    - Ensure that the Cloud Function has appropriate permissions to interact with BigQuery.
    - The 'schema' field is required for CREATE and UPDATE operations but not for DELETE.
    - This function uses the `BigQueryDDL` class to manage BigQuery operations.
    """
    # Initialize a logger for tracking events and errors
    logger = create_logger()

    # Retrieve JSON data from the HTTP request
    request_json = request.get_json(silent=True)
    logger.info(f"Received request: {request_json}")

    # Extract information from the request JSON
    project_id = request_json['project_id']
    dataset_name = request_json['dataset_name']
    dataset_location = request_json['dataset_location']
    table_name = request_json['table_name']
    operation = request_json['operation']
    schema = request_json.get('schema', None)  # Schema is optional for DELETE operations

    # Create a BigQuery client instance for interacting with BigQuery
    client = bigquery.Client(project=project_id)

    # Create an instance of BigQueryDDL for performing DDL operations
    big_query_op = BigQueryDDL(client, project_id, dataset_name, dataset_location, table_name)

    # Determine which operation to perform based on the 'operation' value
    response = {}
    if operation.upper() == "CREATE":
        # Call the create_table method with the provided schema
        response = big_query_op.create_table(schema)
    elif operation.upper() == "UPDATE":
        # Call the update_table_schema method with the new schema
        response = big_query_op.update_table_schema(schema)
    elif operation.upper() == "DELETE":
        # Call the delete_table method to remove the specified table
        response = big_query_op.delete_table()

    # Return the response, which indicates success or error based on the operation's outcome
    return response
