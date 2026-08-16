from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
)


def load_documents(saved_files):

    documents = []

    for file_path in saved_files:

        path = Path(file_path)
        extension = path.suffix.lower()

        try:

            # =========================
            # PDF
            # =========================

            if extension == ".pdf":

                loader = PyPDFLoader(str(path))


            # =========================
            # WORD
            # .docx / .doc
            # =========================

            elif extension in [".docx", ".doc"]:

                loader = UnstructuredWordDocumentLoader(
                    str(path)
                )


            # =========================
            # TEXT
            # =========================

            elif extension == ".txt":

                loader = TextLoader(
                    str(path),
                    encoding="utf-8"
                )


            # =========================
            # EXCEL
            # .xlsx / .xls
            # =========================

            elif extension in [".xlsx", ".xls"]:

                loader = UnstructuredExcelLoader(
                    str(path),
                    mode="elements"
                )


            # =========================
            # CSV
            # =========================

            elif extension == ".csv":

                loader = CSVLoader(
                    str(path)
                )


            # =========================
            # UNSUPPORTED FILE
            # =========================

            else:

                print(
                    f"⚠️ Unsupported file type: {path.name}"
                )

                continue


            # =========================
            # LOAD DOCUMENT
            # =========================

            loaded_documents = loader.load()


            # =========================
            # ADD SOURCE FILE
            # =========================

            for document in loaded_documents:

                document.metadata["source_file"] = str(path)

                document.metadata["file_name"] = path.name

                document.metadata["file_type"] = extension


            documents.extend(loaded_documents)


            print(
                f"✅ Loaded: {path.name}"
            )


        except Exception as error:

            print(
                f"❌ Failed to load {path.name}: {error}"
            )


    return documents