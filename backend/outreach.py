from gmail_service import send_email


def send_outreach(
    contacts,
    generated_email,
    resume_path
):

    results = []

    for contact in contacts:

        try:

            result = send_email(
                to_email=contact.email,
                subject=generated_email.subject,
                body=generated_email.body,
                attachment_path=resume_path
            )

            results.append({
                "email": contact.email,
                "status": "SENT",
                "message_id": result["id"]
            })

        except Exception as e:

            print(f"\nERROR sending to {contact.email}:")
            print(type(e).__name__)
            print(str(e))

            results.append({
                "email": contact.email,
                "status": "FAILED",
                "error": str(e)
            })

    return results