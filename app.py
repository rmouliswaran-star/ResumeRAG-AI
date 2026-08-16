import html
import os
import re
from pathlib import Path

import streamlit as st

from core.ai_engine import ask_ai
from core.document_loader import load_documents
from core.embeddings import create_embeddings
from core.text_splitter import split_documents
from core.upload_manager import save_uploaded_files
from core.vector_db import create_vector_database, load_vector_database


st.set_page_config(
    page_title="ResumeRAG AI",
    page_icon="🧠",
    layout="wide"
)


if os.path.exists("assets/style.css"):
    with open("assets/style.css", "r", encoding="utf-8") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )


if "messages" not in st.session_state:
    st.session_state.messages = []


if "vector_db" not in st.session_state:
    embeddings = create_embeddings()
    st.session_state.vector_db = load_vector_database(embeddings)


def process_files(files):
    with st.spinner("Reading resumes and creating AI database..."):
        saved_files = save_uploaded_files(files)
        documents = load_documents(saved_files)
        chunks = split_documents(documents)
        embeddings = create_embeddings()

        st.session_state.vector_db = create_vector_database(
            chunks,
            embeddings
        )

    st.success("✅ Resume database ready!")


def is_resume_download_request(question):

    question = question.lower().strip()

    download_phrases = [
        "download resume",
        "download the resume",
        "download cv",
        "give me the resume",
        "give me that resume",
        "send me the resume",
        "send the resume",
        "return the resume",
        "provide the resume",
        "get the resume",
        "open the resume"
    ]

    return any(
        phrase in question
        for phrase in download_phrases
    )
    question = question.lower()

    action_words = [
        "give", "show", "download", "send",
        "open", "get", "return", "provide"
    ]

    resume_words = ["resume", "cv", "pdf"]

    return (
        any(word in question for word in action_words)
        and any(word in question for word in resume_words)
    )


def find_requested_resume(vector_db, question):

    documents = vector_db.similarity_search(
        question,
        k=8
    )

    supported_formats = {
        ".pdf",
        ".docx",
        ".doc",
        ".txt",
        ".xlsx",
        ".xls",
        ".csv"
    }

    for document in documents:

        source_file = document.metadata.get(
            "source_file"
        )

        if not source_file:
            continue

        resume_path = Path(source_file)

        if (
            resume_path.exists()
            and resume_path.suffix.lower()
            in supported_formats
        ):
            return resume_path

    return None

st.markdown(
    """
    <div class="logo">
        <span class="red">R</span><span class="white">esume</span><span class="red">RAG</span><span class="white"> AI</span>
    </div>

    <div class="subtitle">
        Match Candidates • Return Resumes
    </div>
    """,
    unsafe_allow_html=True
)


if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="ai">
            🤖 <b>ResumeRAG AI</b>
            <br><br>
            Upload candidate resumes.
            <br><br>
            Ask for the information you need.
            <br><br>
            You can also Request a specific candidate’s resume.
        </div>
        """,
        unsafe_allow_html=True
    )


with st.popover("📎"):
    uploaded_files = st.file_uploader(
        "Add resumes",
        type=[
            "pdf",
            "docx",
            "doc",
            "txt",
            "xlsx",
            "csv"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:
        process_files(uploaded_files)


for message_number, message in enumerate(st.session_state.messages):
    safe_text = html.escape(message["content"]).replace("\n", "<br>")

    if message["role"] == "assistant":
        st.markdown(
            f"""
            <div class="ai">
                🤖 <b>ResumeRAG AI</b>
                <br><br>
                {safe_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        resume_path_text = message.get("resume_path")

        if resume_path_text:
            resume_path = Path(resume_path_text)

            if resume_path.exists():

                mime_types = {
                    ".pdf": "application/pdf",

                    ".docx": (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),

                    ".doc": "application/msword",

                    ".txt": "text/plain",

                    ".xlsx": (
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),

                    ".xls": "application/vnd.ms-excel",

                    ".csv": "text/csv"
                }

                file_extension = resume_path.suffix.lower()

                mime_type = mime_types.get(
                    file_extension,
                    "application/octet-stream"
                )

                with open(resume_path, "rb") as resume_file:

                    st.download_button(
                        label=f"Download {resume_path.name}",
                        data=resume_file.read(),
                        file_name=resume_path.name,
                        mime=mime_type,
                        key=f"download_resume_{message_number}"
                    )

    else:
        st.markdown(
            f"""
            <div class="user">
                {safe_text}
            </div>
            """,
            unsafe_allow_html=True
        )


question = st.chat_input(
    "Enter job requirements, or ask for a candidate's resume..."
)


if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    safe_question = html.escape(question).replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="user">
            {safe_question}
        </div>
        """,
        unsafe_allow_html=True
    )

    answer = ""
    resume_path = None

    with st.spinner("ResumeRAG AI is reviewing the resumes..."):

        if st.session_state.vector_db:

            if is_resume_download_request(question):
                resume_path = find_requested_resume(
                    st.session_state.vector_db,
                    question
                )

                if resume_path:
                    answer = (
                        f"Resume found: {resume_path.name}\n\n"
                        "Use the download button below."
                    )
                else:
                    answer = (
                        "I could not find that candidate's resume "
                        "in the uploaded files."
                    )

            else:
                answer = ask_ai(
                    st.session_state.vector_db,
                    question
                )

        else:
            answer = "Please attach resumes first."

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "resume_path": str(resume_path) if resume_path else None
        }
    )

    st.rerun()