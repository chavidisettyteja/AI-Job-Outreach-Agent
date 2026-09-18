from extractor import extract_file
from analyzer import analyze_text
from resume_selector import select_resume
from email_generator import generate_email
from outreach import send_outreach
from resume_mapper import get_resume_path


FILE_PATH = "test_files/job.txt"


# -------------------------
# PHASE 1
# -------------------------

text = extract_file(FILE_PATH)

analysis = analyze_text(text)

print("\n=== PHASE 1 ===")

print("Contacts:")

for contact in analysis.contacts:
    print(contact.email)

if analysis.job:
    print("Job:", analysis.job.title)


# -------------------------
# PHASE 2
# -------------------------

selection = select_resume(
    analysis
)

print("\n=== PHASE 2 ===")

print("Selected Resume:", selection.resume)
print("Reason:", selection.reason)
print("Matched Skills:", selection.matched_skills)


# -------------------------
# EMAIL GENERATION
# -------------------------

email = generate_email(
    analysis,
    selection
)

print("\n=== GENERATED EMAIL ===")

print("Subject:", email.subject)
print(email.body)


# -------------------------
# RESUME MAPPING
# -------------------------

RESUME_PATH = get_resume_path(
    selection.resume
)

print("\nSelected Resume File:")
print(RESUME_PATH)


# -------------------------
# PHASE 3
# -------------------------

print("\n=== SENDING ===")

results = send_outreach(
    analysis.contacts,
    email,
    RESUME_PATH
)

for result in results:

    print(
        result["email"],
        "→",
        result["status"]
    )