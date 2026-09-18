import os
import base64
import pymupdf
import pandas as pd
import pytesseract

from PIL import Image
from docx import Document


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


def extract_pdf(file_path):

    text = ""

    document = pymupdf.open(file_path)

    for page in document:

        text += page.get_text()

    document.close()

    return text


def extract_docx(file_path):

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:

        text.append(paragraph.text)

    return "\n".join(text)


def extract_csv(file_path):

    dataframe = pd.read_csv(file_path)

    return dataframe.to_string(
        index=False
    )


def extract_xlsx(file_path):

    dataframe = pd.read_excel(file_path)

    return dataframe.to_string(
        index=False
    )


def extract_image(file_path):

    image = Image.open(file_path)

    text = pytesseract.image_to_string(
        image
    )

    return text


def extract_file(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()


    if extension == ".txt":

        return extract_txt(file_path)


    elif extension == ".pdf":

        return extract_pdf(file_path)


    elif extension == ".docx":

        return extract_docx(file_path)


    elif extension == ".csv":

        return extract_csv(file_path)


    elif extension in [
        ".xlsx",
        ".xls"
    ]:

        return extract_xlsx(file_path)


    elif extension in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        return extract_image(file_path)


    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )