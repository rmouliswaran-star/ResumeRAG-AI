import shutil
from pathlib import Path

# -----------------------------
# Resume Folder
# -----------------------------

RESUME_FOLDER = Path("data/resumes")

RESUME_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------
# Save Uploaded Files
# -----------------------------

def save_uploaded_files(uploaded_files):

    saved_files = []

    if not uploaded_files:
        return saved_files

    for uploaded_file in uploaded_files:

        file_path = RESUME_FOLDER / uploaded_file.name

        with open(file_path, "wb") as f:

            f.write(uploaded_file.getbuffer())

        saved_files.append(str(file_path))

    return saved_files


# -----------------------------
# Get Resume List
# -----------------------------

def get_resume_files():

    files = []

    for file in RESUME_FOLDER.glob("*.pdf"):

        files.append(file)

    return sorted(files)


# -----------------------------
# Delete Resume
# -----------------------------

def delete_resume(filename):

    file = RESUME_FOLDER / filename

    if file.exists():

        file.unlink()


# -----------------------------
# Delete All
# -----------------------------

def delete_all_resumes():

    if RESUME_FOLDER.exists():

        shutil.rmtree(RESUME_FOLDER)

    RESUME_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )
