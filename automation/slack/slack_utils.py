from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_slack_notification(data):
    # Slack configuration
    token = 'your_slack_token'
    channel = '#general'

    # Initialize Slack WebClient
    client = WebClient(token=token)

    # Construct message text
    message = f"New webhook data received: {json.dumps(data)}"

    try:
        # Send message to Slack channel
        response = client.chat_postMessage(channel=channel, text=message)
        print('Slack notification sent successfully:', response)
    except SlackApiError as e:
        print('Error sending Slack notification:', e.response['error'])
