import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from schemas import AnalysisResult, ResumeSelection


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

client = Groq(api_key=api_key)


def select_resume(result: AnalysisResult) -> ResumeSelection:

    if not result.job:
        raise ValueError("No job information available for resume selection.")

    job = result.job

    prompt = f"""
You are an AI resume selection agent.

The candidate has exactly three resumes:

1. AI_ENGINEER
2. DATA_ANALYST
3. AML_FRAUD

Your job is to determine which resume is most relevant to the
job opportunity.

JOB INFORMATION:

Title:
{job.title}

Company:
{job.company}

Description:
{job.description}

Skills:
{job.skills}


RESUME PROFILES:

AI_ENGINEER:
- Python
- Java
- FastAPI
- Spring Boot
- React
- MERN
- LangChain
- RAG
- AI/ML
- APIs
- Backend development

DATA_ANALYST:
- SQL
- Excel
- Power BI
- Power Query
- Python
- Pandas
- NumPy
- Data analysis
- Reporting
- Data visualization

AML_FRAUD:
- AML
- KYC
- Fraud detection
- Transaction monitoring
- Payment fraud
- Account takeover
- Risk analysis
- Compliance
- Investigation
- Quality analysis


RULES:

1. Select ONLY one of:
   AI_ENGINEER
   DATA_ANALYST
   AML_FRAUD

2. Compare the actual job requirements against the resume profiles.

3. Do not select a resume merely because of the job title.

4. Consider the job description and required skills.

5. Only claim skills that are explicitly present in the job
   information.

6. matched_skills must contain skills/keywords from the job that
   match the selected resume profile.

7. Give a short explanation for the selection.

8. Return ONLY valid JSON.

Return exactly:

{{
    "resume": "AI_ENGINEER",
    "reason": "short explanation",
    "matched_skills": ["skill1", "skill2"]
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a resume selection agent."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return ResumeSelection.model_validate_json(content)