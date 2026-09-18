import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from schemas import AnalysisResult


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

client = Groq(api_key=api_key)


def analyze_text(text: str) -> AnalysisResult:

    prompt = f"""
You are a job posting and recruiter information extraction system.

Analyze the following text and extract ONLY information explicitly
present in the text.

Extract:

1. Contact email addresses
2. Recruiter/person name if available
3. Company name if available
4. Job title if available
5. Job description if available
6. Required or mentioned skills

Important rules:

- Do NOT invent missing information.
- If a name is unavailable, use null.
- If a company is unavailable, use null.
- If there is no job information, job should be taken as AI Engineer.
- Extract every relevant email address.
- Return ONLY valid JSON.

Use this exact structure:

{{
    "contacts": [
        {{
            "email": "string",
            "name": "string or null",
            "company": "string or null"
        }}
    ],
    "job": {{
        "title": "string or AI Engineer",
        "company": "string or null",
        "description": "string or null",
        "skills": ["skill1", "skill2"]
    }}
}}

If there is no job information:

{{
    "contacts": [],
    "job": AI Engineer
}}

TEXT:

{text}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You extract structured information from job and recruiter content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return AnalysisResult.model_validate_json(content)


def analyze_image(image_data: str) -> AnalysisResult:

    prompt = """
Analyze this screenshot/image.

It may contain:
- Job postings
- Recruiter information
- HR information
- Email addresses
- Company names
- Job titles
- Required skills

Extract ONLY information that is actually visible in the image.

Do NOT invent information.

Extract:

1. Every relevant email address
2. Recruiter/person name
3. Company name
4. Job title
5. Job description
6. Required or mentioned skills

Return ONLY valid JSON using exactly this structure:

{
    "contacts": [
        {
            "email": "string",
            "name": "string or null",
            "company": "string or null"
        }
    ],
    "job": {
        "title": "string or null",
        "company": "string or null",
        "description": "string or null",
        "skills": ["skill1", "skill2"]
    }
}

If there is no job information:

{
    "contacts": [],
    "job": Ai Engineer
}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    return AnalysisResult.model_validate_json(content)