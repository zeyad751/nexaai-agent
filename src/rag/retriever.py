
from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_db"


def get_retriever(project_id: str | None = None):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_PATH),
        embedding_function=embeddings,
    )

    search_kwargs = {"k": 12}

    if project_id is not None:
        search_kwargs["filter"] = {"project_id": project_id}

    retriever = vectorstore.as_retriever(
        search_kwargs=search_kwargs,
    )

    return retriever
