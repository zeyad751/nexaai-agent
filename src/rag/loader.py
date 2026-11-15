from pathlib import Path
from langchain_community.document_loaders import TextLoader


DOCUMENTS_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "documents"
)


def load_documents():
    documents = []

    for file_path in DOCUMENTS_PATH.rglob("*.md"):
        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        loaded_documents = loader.load()

        for document in loaded_documents:
            document.metadata["source"] = str(file_path)
            document.metadata["filename"] = file_path.name

            # If the document is inside a project folder,
            # keep the project ID as metadata.
            if file_path.parent.name.startswith("PRJ-"):
                document.metadata["project_id"] = file_path.parent.name

            documents.append(document)

    return documents