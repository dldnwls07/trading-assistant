# trading_assist/notifications.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, to_email):
    """
    Sends an email using SMTP settings from environment variables.
    """
    # SMTP-related environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
        print("Error: SMTP environment variables not set. Email not sent.")
        print("Please set SMTP_SERVER, SMTP_PORT, SMTP_USER, and SMTP_PASSWORD.")
        return False

    try:
        smtp_port = int(smtp_port)
    except (ValueError, TypeError):
        print(f"Error: Invalid SMTP_PORT: {smtp_port}. Must be an integer.")
        return False

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        print(
            "Please check your SMTP_USER and SMTP_PASSWORD "
            "(e.g., App Password for Gmail)."
        )
        return False
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
        return False


if __name__ == "__main__":
    # Example usage for direct testing of this module
    # Before running, make sure to set your environment variables, for example:
    # export SMTP_SERVER="smtp.gmail.com"
    # export SMTP_PORT="587"
    # export SMTP_USER="your_email@gmail.com"
    # export SMTP_PASSWORD="your_app_password"  # pragma: allowlist secret
    # export RECIPIENT_EMAIL="recipient_email@example.com"

    print("Running notification module test...")
    recipient = os.getenv("RECIPIENT_EMAIL")
    if not recipient:
        print("RECIPIENT_EMAIL environment variable not set. Cannot send test email.")
    else:
        test_subject = "Trading Assistant - Test Email"
        test_body = "This is a test email from the trading_assist.notifications module."
        send_email(test_subject, test_body, recipient)
