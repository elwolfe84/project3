import os
import subprocess
from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage

# Email Configuration
SMTP_SERVER = "smtp.turnanewleaf.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "alerts@turnanewleaf.com"
# EMAIL_PASSWORD =
RECIPIENT_EMAIL = "logs@turnanewleaf.com"

# Define the output directory and file
output_directory = r"C:\failedlogs"
output_file = "FailedLoginAttempts.txt"
output_path = os.path.join(output_directory, output_file)

# Ensure the output directory exists
try:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
except Exception as e:
    print(f"Error creating directory {output_directory}: {e}")
    exit(1)

# Calculate the timestamp for 30 minutes ago
time_30_minutes_ago = (datetime.now(timezone.utc) - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

# Debug: Print the generated timestamp
print(f"Generated timestamp for query: {time_30_minutes_ago}")

# Command to fetch failed login attempts (Event ID 4625) from the last 30 minutes
command = (
    f'wevtutil qe Security /q:"*[System[(EventID=4625) and TimeCreated[@SystemTime>=\'{time_30_minutes_ago}\']]]" /f:text'
)

# Debug: Print the command being executed
print(f"Executing command: {command}")

# Run the command and capture the output
try:
    result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
    failed_logins = result.stdout.strip()  # Remove extra whitespace
    print(f"Command executed successfully. Output length: {len(failed_logins)}")
except subprocess.CalledProcessError as e:
    print(f"Error fetching log data: {e}")
    failed_logins = ""

# Write the output to the file and decide if email should be sent
email_triggered = False
try:
    with open(output_path, "w", encoding="utf-8") as file:
        if failed_logins:
            file.write(failed_logins)
            print(f"Failed login attempts saved to {output_path}")
            email_triggered = True  # Trigger email only when failed attempts are found
        else:
            no_attempts_message = "No failed login attempts were made in the last 30 minutes."
            file.write(no_attempts_message)
            print(no_attempts_message)
except Exception as e:
    print(f"Error writing to file {output_path}: {e}")
    exit(1)

# Function to send the email
def send_email(file_path):
    try:
        # Create the email message
        msg = EmailMessage()
        msg["Subject"] = "Failed Login Attempts Report"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("Attached is the report of failed login attempts from the last 30 minutes.")

        # Attach the file
        with open(file_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="text", subtype="plain", filename=output_file)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Send the email only if there are failed login attempts
if email_triggered:
    send_email(output_path)