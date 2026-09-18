import os
import base64
import mimetypes

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


# BASE_DIR = os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))
# )

# CREDENTIALS_FILE = os.path.join(
#     BASE_DIR,
#     "credentials.json"
# )

# TOKEN_FILE = os.path.join(
#     BASE_DIR,
#     "token.json"
# )
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.exists("/etc/secrets/credentials.json"):
    CREDENTIALS_FILE = "/etc/secrets/credentials.json"
else:
    CREDENTIALS_FILE = os.path.join(
        os.path.dirname(BASE_DIR),
        "credentials.json"
    )

if os.path.exists("/etc/secrets/token.json"):
    TOKEN_FILE = "/etc/secrets/token.json"
else:
    TOKEN_FILE = os.path.join(
        os.path.dirname(BASE_DIR),
        "token.json"
    )


def get_gmail_service():

    creds = None

    if os.path.exists(TOKEN_FILE):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


def send_email(
    to_email,
    subject,
    body,
    attachment_path=None
):

    service = get_gmail_service()

    message = EmailMessage()

    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    if attachment_path:

        mime_type, _ = mimetypes.guess_type(
            attachment_path
        )

        if mime_type is None:
            mime_type = "application/octet-stream"

        main_type, sub_type = mime_type.split("/", 1)

        with open(attachment_path, "rb") as file:

            file_data = file.read()

        message.add_attachment(
            file_data,
            maintype=main_type,
            subtype=sub_type,
            filename=os.path.basename(attachment_path)
        )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_body = {
        "raw": encoded_message
    }

    result = service.users().messages().send(
        userId="me",
        body=send_body
    ).execute()

    return result