from pathlib import Path

from langchain_community.vectorstores import FAISS


VECTOR_DB = Path("data/vectorstore")


def create_vector_database(chunks, embeddings):

    db = FAISS.from_documents(

        chunks,

        embeddings

    )

    VECTOR_DB.mkdir(

        parents=True,

        exist_ok=True

    )

    db.save_local(

        str(VECTOR_DB)

    )

    return db


def load_vector_database(embeddings):

    if not VECTOR_DB.exists():

        return None

    try:

        return FAISS.load_local(

            str(VECTOR_DB),

            embeddings,

            allow_dangerous_deserialization=True

        )

    except Exception:

        return None
