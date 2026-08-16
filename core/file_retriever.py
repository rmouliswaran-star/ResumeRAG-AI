import os
import re
from pathlib import Path


RESUME_FOLDER = "data/resumes"


# ---------------------------------
# Supported resume formats
# ---------------------------------

SUPPORTED_FORMATS = {
    ".pdf",
    ".docx",
    ".doc",
    ".txt",
    ".xlsx",
    ".xls",
    ".csv",
}


# ---------------------------------
# Clean text
# ---------------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9 ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ---------------------------------
# Find Resume
# ---------------------------------

def find_resume(question):

    """
    Find an uploaded resume based on the
    candidate name mentioned in the question.

    Supports:
        PDF
        DOCX
        DOC
        TXT
        XLSX
        XLS
        CSV
    """

    if not os.path.exists(RESUME_FOLDER):
        return None


    # ---------------------------------
    # Get supported files
    # ---------------------------------

    files = [

        file

        for file in os.listdir(RESUME_FOLDER)

        if Path(file).suffix.lower()
        in SUPPORTED_FORMATS

    ]


    if not files:
        return None


    question_text = clean_text(question)


    # ---------------------------------
    # Words to ignore
    # ---------------------------------

    ignore_words = {

        "give",
        "me",
        "the",
        "resume",
        "resumes",
        "cv",
        "of",
        "show",
        "download",
        "send",
        "provide",
        "get",
        "open",
        "return",
        "candidate",
        "candidates",
        "please",
        "can",
        "you",
        "i",
        "want",
        "to",
        "for",
        "a",
        "an",

    }


    words = [

        word

        for word in question_text.split()

        if word not in ignore_words

    ]


    # ---------------------------------
    # Find best candidate
    # ---------------------------------

    best_match = None

    highest_score = 0


    for file in files:

        filename = Path(file).stem

        filename = clean_text(filename)


        score = 0


        for word in words:

            if len(word) < 2:
                continue


            if word in filename:

                score += 1


        # Exact filename phrase bonus

        if filename and filename in question_text:

            score += 5


        if score > highest_score:

            highest_score = score

            best_match = file


    # ---------------------------------
    # Return path
    # ---------------------------------

    if best_match:

        return os.path.join(
            RESUME_FOLDER,
            best_match
        )


    return None