from google.cloud import bigquery
import traceback
from common_utils.utils import create_logger, json_reader


class BigQueryDDL:
    def __init__(self, client, project_id, dataset_name, dataset_location, table_name):
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.dataset_location = dataset_location
        self.table_name = table_name
        self.logger = create_logger()

    def create_table(self, schema):
        try:
            dataset = bigquery.Dataset(f"{self.client.project}.{self.dataset_name}")
            dataset.location = self.dataset_location
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            self.logger.info("Created dataset {}.{}".format(self.project_id, dataset.dataset_id))

            # Convert the JSON schema to a list of BigQuery schema fields
            bigquery_schema = [bigquery.SchemaField(**field) for field in schema]

            # Construct the table reference
            table_ref = self.client.dataset(dataset.dataset_id).table(self.table_name)

            # Define the table object with schema
            table = bigquery.Table(table_ref, schema=bigquery_schema)

            # Create the table in BigQuery
            table = self.client.create_table(table)
            self.logger.info(
                f"Table {table.full_table_id} created successfully in {self.dataset_name} dataset under {self.project_id} project.")

        except Exception as error:
            self.logger.error(f"Error Creating table : {error}")
            raise Exception(f"Error Traceback: {traceback.format_exc()}")
