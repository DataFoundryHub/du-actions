from google.cloud import bigquery
import traceback
from common_utils.utils import create_logger, json_reader


# Class to handle BigQuery DDL operations
class BigQueryDDL:
    def __init__(self, client, project_id, dataset_name, dataset_location, table_name):
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.dataset_location = dataset_location
        self.table_name = table_name
        self.logger = create_logger()

    def create_table(self, schema):
        """Create a BigQuery table with the specified schema."""
        try:
            # Ensure the dataset exists
            dataset_ref = f"{self.client.project}.{self.dataset_name}"
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.dataset_location
            self.client.create_dataset(dataset, exists_ok=True)

            self.logger.info(f"Created dataset {self.project_id}.{self.dataset_name} or it already exists.")

            # Convert the schema to BigQuery fields
            bigquery_schema = [bigquery.SchemaField(key,value) for key,value in schema.items()]

            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Create the table with schema
            table = bigquery.Table(table_ref, schema=bigquery_schema)

            # Create the table (use exists_ok=True to avoid errors if it already exists)
            self.client.create_table(table, exists_ok=True)

            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} created successfully.")

        except Exception as error:
            self.logger.error(f"Error creating table: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            raise  # Re-raise to retain context

    def delete_table(self):
        """Delete the specified BigQuery table."""
        try:
            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Delete the table
            self.client.delete_table(table_ref, not_found_ok=True)

            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} deleted successfully.")

        except Exception as error:
            self.logger.error(f"Error deleting table: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            raise

    def update_table(self, new_schema):
        """Update the schema of the specified BigQuery table."""
        try:
            # Convert the new schema to BigQuery fields
            bigquery_schema = [bigquery.SchemaField(key,value) for key,value in new_schema.items()]

            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Get the existing table
            table = self.client.get_table(table_ref)

            # Update the schema (appending new fields or modifying existing ones)
            table.schema = bigquery_schema

            # Update the table in BigQuery
            self.client.update_table(table, ["schema"])

            self.logger.info(f"Schema for table {self.project_id}.{self.dataset_name}.{self.table_name} updated successfully.")

        except Exception as error:
            self.logger.error(f"Error updating table schema: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            raise
