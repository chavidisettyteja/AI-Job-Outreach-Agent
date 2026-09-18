import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from schemas import AnalysisResult, ResumeSelection, GeneratedEmail


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

api_key = os.getenv("GROQ_API_KEY")
candidate_name = os.getenv("CANDIDATE_NAME")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

if not candidate_name:
    raise ValueError("CANDIDATE_NAME was not found in .env")

client = Groq(api_key=api_key)


def generate_email(
    result: AnalysisResult,
    resume_selection: ResumeSelection
):

    if not result.job:
        raise ValueError("No job information available.")

    job = result.job

    recruiter_name = None

    if result.contacts:
        recruiter_name = result.contacts[0].name

    prompt = f"""
You are a professional job application email writer.

Write a concise and professional job application email.

IMPORTANT:
You must NOT invent candidate experience, achievements,
years of experience, projects, responsibilities, employers,
certifications, or technical accomplishments.

The candidate's skills below are the ONLY candidate information
you are allowed to mention.

CANDIDATE NAME:
{candidate_name}

CANDIDATE SKILLS:
{resume_selection.matched_skills}

SELECTED RESUME:
{resume_selection.resume}

JOB TITLE:
{job.title}

COMPANY:
{job.company}

JOB DESCRIPTION:
{job.description}

JOB SKILLS:
{job.skills}

RECRUITER:
{recruiter_name}


RULES:

1. Mention the job title.

2. Mention the company if available.

3. Mention only skills contained in the candidate's
matched skills list.

4. Do NOT say:
   - "I have hands-on experience"
   - "I worked extensively"
   - "I built"
   - "I developed"
   - "I led"
   - "I achieved"
   - "I have X years of experience"

   unless that exact information is explicitly provided
   in the input.

5. You may say:
   "My skills in X, Y and Z align with the requirements
   of this role."

6. Keep the email around 100-140 words.

7. Do not mention the resume-selection process.

8. Do not invent recruiter information.

9. The resume will be attached separately.

10. End the email exactly with:

Best regards,
{candidate_name}

11. Do NOT use [Your Name].

12. Return ONLY valid JSON.

Use exactly:

{{
    "subject": "Application for <job title> Role",
    "body": "email body"
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write factual, concise job application emails. "
                    "Never invent candidate information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    return GeneratedEmail.model_validate_json(content)