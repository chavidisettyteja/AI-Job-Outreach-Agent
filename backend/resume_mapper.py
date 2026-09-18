from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


RESUME_MAP = {
    "AI_ENGINEER": BASE_DIR / "resumes" / "Chavidisetti_AI_Engineer(AW).pdf",
    "DATA_ANALYST": BASE_DIR / "resumes" / "Chavidisetti_Data_Analyst.pdf",
    "AML_FRAUD": BASE_DIR / "resumes" / "Chavidisetti_AML_KYC.pdf",
}


def get_resume_path(resume_type):

    if resume_type not in RESUME_MAP:
        raise ValueError(
            f"Unknown resume type: {resume_type}"
        )

    resume_path = RESUME_MAP[resume_type]

    if not resume_path.exists():
        raise FileNotFoundError(
            f"Resume not found: {resume_path}"
        )

    return str(resume_path)