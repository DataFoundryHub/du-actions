from google.cloud import bigquery


def write_to_bigquery(data):
    # Initialize BigQuery client
    client = bigquery.Client()

    # Define dataset ID and table ID
    dataset_id = 'your_dataset_id'
    table_id = 'your_table_id'

    # Construct BigQuery table reference
    table_ref = client.dataset(dataset_id).table(table_id)

    # Load data into BigQuery table
    rows_to_insert = [(data['value1'], data['value2'])]  # Customize based on your data
    errors = client.insert_rows(table_ref, rows_to_insert)

    if errors == []:
        print('Data loaded into BigQuery table successfully.')
    else:
        print('Errors occurred while inserting rows:', errors)
