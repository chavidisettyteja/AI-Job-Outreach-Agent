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


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==============================
# LOCAL / RENDER CREDENTIAL PATH
# ==============================

RENDER_CREDENTIALS = "/etc/secrets/credentials.json"
RENDER_TOKEN = "/etc/secrets/token.json"


if os.path.exists(RENDER_CREDENTIALS):
    CREDENTIALS_FILE = RENDER_CREDENTIALS
else:
    CREDENTIALS_FILE = os.path.join(
        os.path.dirname(BASE_DIR),
        "credentials.json"
    )


if os.path.exists(RENDER_TOKEN):
    TOKEN_FILE = RENDER_TOKEN
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
            token.write(
                creds.to_json()
            )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


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

        main_type, sub_type = mime_type.split(
            "/",
            1
        )

        with open(
            attachment_path,
            "rb"
        ) as file:

            file_data = file.read()

        message.add_attachment(
            file_data,
            maintype=main_type,
            subtype=sub_type,
            filename=os.path.basename(
                attachment_path
            )
        )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message
        }
    ).execute()

    return result