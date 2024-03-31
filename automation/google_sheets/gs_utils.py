from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def write_to_google_spreadsheet(data):
    # Load Google Sheets credentials
    creds = Credentials.from_authorized_user_file('credentials.json')

    # If credentials are not valid, prompt user to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/spreadsheets'])
            creds = flow.run_local_server(port=0)

    # Build Google Sheets API service
    service = build('sheets', 'v4', credentials=creds)

    # Specify spreadsheet ID and range
    spreadsheet_id = 'your_spreadsheet_id'
    range_name = 'Sheet1!A1'

    # Example data to write
    values = [
        [data['value1'], data['value2']]
    ]

    # Call the Sheets API to update data
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

    print('Data updated successfully:', result)
