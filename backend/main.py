import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from extractor import extract_file
from analyzer import analyze_text, analyze_image
from resume_selector import select_resume
from email_generator import generate_email
from pydantic import BaseModel
from outreach import send_outreach
from resume_mapper import get_resume_path
from schemas import ResumeSelection, GeneratedEmail


app = FastAPI(
    title="AI Job Outreach Agent",
    description="AI-powered job outreach automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-job-outreach-agent.onrender.com/",
        "https://ai-job-outreach-agent.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class SendRequest(BaseModel):

    contacts: list[str]

    subject: str

    body: str

    resume_type: str

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():

    return {
        "message": "AI Job Outreach Agent API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    try:

        print("\n==============================")
        print("ANALYZE REQUEST")
        print("==============================")

        print("Filename:", file.filename)

        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        print("File saved:", file_path)

        extension = Path(
            file.filename
        ).suffix.lower()

        print("File type:", extension)


        # -----------------------------------------
        # IMAGE
        # -----------------------------------------

        if extension in [
            ".png",
            ".jpg",
            ".jpeg"
        ]:

            print("Processing image with OCR...")

            extracted_text = extract_file(
                str(file_path)
            )

            print("\nOCR TEXT:")
            print(extracted_text)

            analysis = analyze_text(
                extracted_text
            )

            print("OCR analysis completed.")

        # -----------------------------------------
        # OTHER FILES
        # -----------------------------------------

        else:

            print("Extracting text...")

            extracted_text = extract_file(
                str(file_path)
            )

            print("Text extraction completed.")

            analysis = analyze_text(
                extracted_text
            )


        print("Contacts found:", len(analysis.contacts))

        if analysis.job:
            print("Job found:", analysis.job.title)

            selection = select_resume(analysis)

            print("Resume selected:", selection.resume)

            generated_email = generate_email(
                analysis,
                selection
            )

            print("Email generated.")

        else:
            print("No job information found.")
            print("Defaulting to AI_ENGINEER resume.")

            selection = ResumeSelection(
                resume="AI_ENGINEER",
                reason="No specific job information was provided. Defaulting to the AI Engineer resume.",
                matched_skills=[
                    "Python",
                    "Java",
                    "FastAPI",
                    "Spring Boot",
                    "React",
                    "MERN",
                    "LangChain",
                    "RAG",
                    "AI/ML",
                    "APIs",
                    "Backend development"
                ]
            )

            generated_email = GeneratedEmail(
                subject="Application for AI Engineer Opportunities",
                body="""Dear Hiring Team,

        I am reaching out to explore AI Engineer opportunities at your organization.

        My skills include Python, Java, FastAPI, Spring Boot, React, MERN, LangChain, RAG, AI/ML, APIs, and backend development. I am interested in opportunities where I can apply these skills and contribute to AI-driven and software engineering initiatives.

        I have attached my AI Engineer resume for your consideration. I would be grateful if you could consider my profile for any relevant current or upcoming opportunities.

        Thank you for your time and consideration.

        Best regards,
        NAGA SAI TEJASWI KUMAR"""
            )

            print("Default AI Engineer email generated.")


        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

        return {

            "contacts": [

                {
                    "email": contact.email,
                    "name": contact.name,
                    "company": contact.company
                }

                for contact in analysis.contacts

            ],

            "job": (

                {
                    "title": analysis.job.title,
                    "company": analysis.job.company,
                    "description": analysis.job.description,
                    "skills": analysis.job.skills
                }

                if analysis.job

                else None

            ),

            "resume_selection": (

                {
                    "resume": selection.resume,
                    "reason": selection.reason,
                    "matched_skills": selection.matched_skills
                }

                if selection

                else None

            ),

            "email": (

                {
                    "subject": generated_email.subject,
                    "body": generated_email.body
                }

                if generated_email

                else None

            )

        }


    except Exception as e:

        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ANALYZE ERROR")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )

    
@app.post("/send")
def send(request: SendRequest):

    resume_path = get_resume_path(
        request.resume_type
    )

    class Contact:
        def __init__(self, email):
            self.email = email

    contacts = [
        Contact(email)
        for email in request.contacts
    ]

    class GeneratedEmail:
        def __init__(self, subject, body):
            self.subject = subject
            self.body = body

    generated_email = GeneratedEmail(
        request.subject,
        request.body
    )

    results = send_outreach(
        contacts,
        generated_email,
        resume_path
    )

    return {
        "results": results
    }


class TextRequest(BaseModel):
    text: str


@app.post("/analyze-text")
def analyze_pasted_text(request: TextRequest):
    try:
        print("\n==============================")
        print("PASTED TEXT ANALYSIS")
        print("==============================")

        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Pasted text cannot be empty."
            )

        print("Analyzing pasted text...")

        analysis = analyze_text(request.text)

        print("Contacts found:", len(analysis.contacts))

        if analysis.job:
            print("Job found:", analysis.job.title)

            selection = select_resume(analysis)

            print("Resume selected:", selection.resume)

            generated_email = generate_email(
                analysis,
                selection
            )

            print("Email generated.")

        else:
            print("No job information found.")
            print("Defaulting to AI_ENGINEER resume.")

            selection = ResumeSelection(
                resume="AI_ENGINEER",
                reason="No specific job information was provided. Defaulting to the AI Engineer resume.",
                matched_skills=[
                    "Python",
                    "Java",
                    "FastAPI",
                    "Spring Boot",
                    "React",
                    "MERN",
                    "LangChain",
                    "RAG",
                    "AI/ML",
                    "APIs",
                    "Backend development"
                ]
            )

            generated_email = GeneratedEmail(
                subject="Application for AI Engineer Opportunities",
                body="""Dear Hiring Team,

I am reaching out to explore AI Engineer opportunities at your organization.

My skills include Python, Java, FastAPI, Spring Boot, React, MERN, LangChain, RAG, AI/ML, APIs, and backend development. I am interested in opportunities where I can apply these skills and contribute to AI-driven and software engineering initiatives.

I have attached my AI Engineer resume for your consideration. I would be grateful if you could consider my profile for any relevant current or upcoming opportunities.

Thank you for your time and consideration.

Best regards,
NAGA SAI TEJASWI KUMAR"""
            )

            print("Default AI Engineer email generated.")

        return {
            "contacts": [
                {
                    "email": contact.email,
                    "name": contact.name,
                    "company": contact.company
                }
                for contact in analysis.contacts
            ],

            "job": (
                {
                    "title": analysis.job.title,
                    "company": analysis.job.company,
                    "description": analysis.job.description,
                    "skills": analysis.job.skills
                }
                if analysis.job else None
            ),

            "resume_selection": {
                "resume": selection.resume,
                "reason": selection.reason,
                "matched_skills": selection.matched_skills
            },

            "email": {
                "subject": generated_email.subject,
                "body": generated_email.body
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("PASTED TEXT ERROR")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )