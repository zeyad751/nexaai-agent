from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from src.rag.loader import load_documents



load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_db"


def build_vector_store():
    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small",api_key=os.getenv("OPENAI_API_KEY"))

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_PATH)
    )

    return vector_store