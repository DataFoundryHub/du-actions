import functions_framework
from google.cloud import bigquery
from common_utils.utils import create_logger
from big_query_ops import BigQueryDDL


@functions_framework.http
def trigger_bq(request):
    request_json = request.get_json(silent=True)
    project_id = request_json['project_id']
    dataset_name = request_json['dataset_name']
    dataset_location = request_json['dataset_location']
    table_name = request_json['table_name']
    operation = request_json['operation']
    schema = request_json['schema']
    client = bigquery.Client(project=project_id)
    big_query_op = BigQueryDDL(client, project_id, dataset_name, dataset_location, table_name)
    response = {}
    if operation.upper() == "CREATE":
        response = big_query_op.create_table(schema)
    if operation.upper() == "UPDATE":
        response = big_query_op.update_table(schema)
    if operation.upper() == "DELETE":
        response = big_query_op.delete_table()
    return response


