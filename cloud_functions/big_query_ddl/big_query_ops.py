from google.cloud import bigquery
import traceback
from common_utils.utils import create_logger, json_reader
from flask import request, jsonify


# Class to handle BigQuery DDL operations
class BigQueryDDL:
    def __init__(self, client, project_id, dataset_name, dataset_location, table_name):
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.dataset_location = dataset_location
        self.table_name = table_name
        self.logger = create_logger()
        self.logger.info("BigQueryDDL instance initialized.")

    def create_table(self, schema):
        """Create a BigQuery table with the specified schema."""
        self.logger.info(f"Creating table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Ensure the dataset exists
            dataset_ref = f"{self.client.project}.{self.dataset_name}"
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.dataset_location

            self.logger.info(f"Creating dataset {self.dataset_name} if not already created.")
            self.client.create_dataset(dataset, exists_ok=True)

            self.logger.info(f"Dataset {self.project_id}.{self.dataset_name} created or already exists.")

            # Convert the schema to BigQuery fields
            bigquery_schema = [bigquery.SchemaField(key, value) for key, value in schema.items()]

            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Create the table with schema
            self.logger.info(f"Creating table {self.table_name} with given schema.")
            table = bigquery.Table(table_ref, schema=bigquery_schema)

            # Create the table (use exists_ok=True to avoid errors if it already exists)
            self.client.create_table(table, exists_ok=True)

            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} created successfully.")
            return {"status": "success", "message": "Table Created successfully."}
        except Exception as error:
            self.logger.error(f"Error creating table {self.table_name}: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": "An internal error occurred."}), 500

    def delete_table(self):
        """Delete the specified BigQuery table."""
        self.logger.info(f"Deleting table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Delete the table
            self.client.delete_table(table_ref, not_found_ok=True)

            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} deleted successfully.")
            return {"status": "success", "message": "Table Deleted successfully."}
        except Exception as error:
            self.logger.error(f"Error deleting table {self.table_name}: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": "An internal error occurred."}), 500

    def update_table(self, new_schema):
        """Update the schema of the specified BigQuery table."""
        self.logger.info(f"Updating schema for table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Convert the new schema to BigQuery fields
            bigquery_schema = [bigquery.SchemaField(key, value) for key, value in new_schema.items()]

            # Construct the table reference
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Get the existing table
            self.logger.info(f"Retrieving table {self.table_name} to update schema.")
            table = self.client.get_table(table_ref)

            # Update the schema (appending new fields or modifying existing ones)
            self.logger.info(f"Applying new schema to table {self.table_name}.")
            table.schema = bigquery_schema

            # Update the table in BigQuery
            self.client.update_table(table, ["schema"])

            self.logger.info(
                f"Schema for table {self.project_id}.{self.dataset_name}.{self.table_name} updated successfully.")
            return {"status": "success", "message": "Table Schema Updated successfully."}
        except Exception as error:
            self.logger.error(f"Error updating table schema {self.table_name}: {error}")
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": "An internal error occurred."}), 500
