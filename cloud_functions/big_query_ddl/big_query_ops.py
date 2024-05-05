from google.cloud import bigquery
import traceback
from common_utils.utils import create_logger, json_reader
from flask import request, jsonify


# Class to manage DDL operations for BigQuery
class BigQueryDDL:
    """
    This class provides methods to create, delete, and update BigQuery tables' schemas.
    It encapsulates common DDL operations and handles logging for audit and debugging.
    """

    def __init__(self, client, project_id, dataset_name, dataset_location, table_name):
        """
        Constructor to initialize BigQueryDDL class with given project information and table details.

        Args:
        - client (bigquery.Client): BigQuery client instance.
        - project_id (str): Google Cloud project ID.
        - dataset_name (str): Name of the BigQuery dataset.
        - dataset_location (str): Location of the dataset, typically 'US' or 'EU'.
        - table_name (str): Name of the BigQuery table.
        """
        # Initialize instance variables with provided parameters
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.dataset_location = dataset_location
        self.table_name = table_name

        # Initialize a logger for recording events
        self.logger = create_logger()
        self.logger.info("BigQueryDDL instance initialized.")

    def create_table(self, schema):
        """
        Creates a new BigQuery table with the specified schema.

        If the dataset does not exist, it will be created. The schema is provided as a dictionary
        where keys represent field names, and values represent data types (e.g., 'STRING', 'INTEGER').

        Args:
        - schema (dict): Dictionary defining the schema for the new table.

        Returns:
        - dict: Status and message indicating success or failure.
        - or a Flask `jsonify` object indicating an error, with HTTP status 500.
        """
        # Log the start of table creation
        self.logger.info(f"Creating table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Ensure the dataset exists
            dataset_ref = f"{self.client.project}.{self.dataset_name}"
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.dataset_location

            # Create dataset if not already present
            self.logger.info(f"Creating dataset {self.dataset_name} if not already present.")
            self.client.create_dataset(dataset, exists_ok=True)

            self.logger.info(f"Dataset {self.project_id}.{self.dataset_name} created or already exists.")

            # Convert the schema into BigQuery schema fields
            bigquery_schema = [bigquery.SchemaField(k, v) for k, v in schema.items()]

            # Reference the desired table within the dataset
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Create the table with the provided schema
            self.logger.info(f"Creating table {self.table_name} with specified schema.")
            table = bigquery.Table(table_ref, schema=bigquery_schema)

            # Create the table with exists_ok=True to avoid errors if it already exists
            self.client.create_table(table, exists_ok=True)

            # Log success and return a success message
            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} created successfully.")
            return {"status": "success", "message": "Table created successfully."}

        except Exception as error:
            # Log error message and traceback, and return an error response
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": f"An internal error occurred. Reason - {error}"}), 500

    def delete_table(self):
        """
        Deletes a BigQuery table.

        If the specified table does not exist, it does not raise an error. This operation will clean up any existing table,
        and is useful for managing resources.

        Returns:
        - dict: Status and message indicating success or failure.
        - or a Flask `jsonify` object indicating an error, with HTTP status 500.
        """
        # Log the start of table deletion
        self.logger.info(f"Deleting table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Reference the table to delete
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Delete the table, not raising errors if not found
            self.client.delete_table(table_ref, not_found_ok=True)

            # Log success and return a success message
            self.logger.info(f"Table {self.project_id}.{self.dataset_name}.{self.table_name} deleted successfully.")
            return {"status": "success", "message": "Table deleted successfully."}

        except Exception as error:
            # Log error message and traceback, and return an error response
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": f"An internal error occurred. Reason - {error}"}), 500

    def update_table_schema(self, new_schema):
        """
        Updates the schema of an existing BigQuery table with a new schema.

        This operation replaces the existing schema with the new one provided in `new_schema`.

        Args:
        - new_schema (dict): Dictionary representing the updated schema.

        Returns:
        - dict: Status and message indicating success or failure.
        - or a Flask `jsonify` object indicating an error, with HTTP status 500.
        """
        # Log the start of schema update
        self.logger.info(f"Updating schema for table {self.table_name} in dataset {self.dataset_name}.")

        try:
            # Convert new schema into BigQuery schema fields
            bigquery_schema = [bigquery.SchemaField(k, v) for k, v in new_schema.items()]

            # Reference the desired table within the dataset
            table_ref = self.client.dataset(self.dataset_name).table(self.table_name)

            # Retrieve the existing table to update its schema
            self.logger.info(f"Retrieving table {self.table_name} to update schema.")
            table = self.client.get_table(table_ref)

            # Update the schema with the new values
            self.logger.info(f"Applying new schema to table {self.table_name}.")
            table.schema = bigquery_schema

            # Update the table's schema in BigQuery
            self.client.update_table(table, ["schema"])

            # Log success and return a success message
            self.logger.info(
                f"Schema for table {self.project_id}.{self.dataset_name}.{self.table_name} updated successfully."
            )
            return {"status": "success", "message": "Table schema updated successfully."}

        except Exception as error:
            # Log error message and traceback, and return an error response
            self.logger.error(f"Error Traceback: {traceback.format_exc()}")
            return jsonify({"status": "error", "message": f"An internal error occurred. Reason - {error}"}), 500
