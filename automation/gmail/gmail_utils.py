import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(data):
    # Email configuration
    sender_email = 'your_sender_email@gmail.com'
    receiver_email = 'your_receiver_email@gmail.com'
    password = 'your_email_password'

    # Create message object
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = f"DATA UPDATE - {}"

    # Create email body
    body = f"""
    Hello,
    Data received from webhook is updated in 
    Here is the data received from the webhook:
    {json.dumps(data, indent=4)}

    Regards,
    Your Cloud Function
    """
    message.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server and send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print('Email sent successfully!')
