import os
import base64
import mimetypes

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(BASE_DIR)


# ==========================================
# CREDENTIAL LOCATIONS
# ==========================================

LOCAL_CREDENTIALS = os.path.join(
    PROJECT_ROOT,
    "credentials.json"
)

LOCAL_TOKEN = os.path.join(
    PROJECT_ROOT,
    "token.json"
)

RENDER_CREDENTIALS = "/etc/secrets/credentials.json"
RENDER_TOKEN = "/etc/secrets/token.json"


# ==========================================
# SELECT CREDENTIAL FILE
# ==========================================

if os.path.exists(RENDER_CREDENTIALS):
    CREDENTIALS_FILE = RENDER_CREDENTIALS
else:
    CREDENTIALS_FILE = LOCAL_CREDENTIALS


if os.path.exists(RENDER_TOKEN):
    TOKEN_FILE = RENDER_TOKEN
else:
    TOKEN_FILE = LOCAL_TOKEN


# ==========================================
# GMAIL SERVICE
# ==========================================

def get_gmail_service():

    print("================================")
    print("GMAIL AUTHENTICATION")
    print("================================")

    print(
        "Credentials file:",
        CREDENTIALS_FILE
    )

    print(
        "Credentials exists:",
        os.path.exists(CREDENTIALS_FILE)
    )

    print(
        "Token file:",
        TOKEN_FILE
    )

    print(
        "Token exists:",
        os.path.exists(TOKEN_FILE)
    )

    creds = None

    # --------------------------------------
    # Load existing token
    # --------------------------------------

    if os.path.exists(TOKEN_FILE):

        print("Loading Gmail token...")

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # --------------------------------------
    # Refresh expired token
    # --------------------------------------

    if creds and creds.expired and creds.refresh_token:

        print("Refreshing Gmail token...")

        creds.refresh(Request())

        # Only write locally.
        # Render Secret Files are read-only.

        if not TOKEN_FILE.startswith("/etc/secrets/"):

            with open(
                TOKEN_FILE,
                "w"
            ) as token:

                token.write(
                    creds.to_json()
                )

    # --------------------------------------
    # No valid token
    # --------------------------------------

    if not creds or not creds.valid:

        raise RuntimeError(
            "Gmail authentication token is missing or invalid. "
            "Please provide a valid token.json in Render Secret Files."
        )

    print("Gmail authentication successful.")

    # --------------------------------------
    # Build Gmail API service
    # --------------------------------------

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


# ==========================================
# SEND EMAIL
# ==========================================

def send_email(
    to_email,
    subject,
    body,
    attachment_path=None
):

    print("================================")
    print("SENDING EMAIL")
    print("================================")

    print("Recipient:", to_email)
    print("Subject:", subject)

    service = get_gmail_service()

    message = EmailMessage()

    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    # --------------------------------------
    # Attachment
    # --------------------------------------

    if attachment_path:

        print(
            "Attachment:",
            attachment_path
        )

        if not os.path.exists(attachment_path):

            raise FileNotFoundError(
                f"Resume attachment not found: {attachment_path}"
            )

        mime_type, _ = mimetypes.guess_type(
            attachment_path
        )

        if mime_type is None:

            mime_type = (
                "application/octet-stream"
            )

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

    # --------------------------------------
    # Encode email
    # --------------------------------------

    encoded_message = (
        base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()
    )

    # --------------------------------------
    # Send through Gmail API
    # --------------------------------------

    result = (
        service
        .users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": encoded_message
            }
        )
        .execute()
    )

    print(
        "Email sent successfully."
    )

    print(
        "Message ID:",
        result.get("id")
    )

    return result