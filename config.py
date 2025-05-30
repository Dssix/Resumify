import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== PATH CONFIGURATION ==========
# Folder containing raw documents
DATA_DIR = "data/"

# Directory where vector index will be stored (Chroma will use this)
INDEX_DIR = "vector_index/"

# Folder for uploaded resumes
UPLOAD_FOLDER = "uploads/"

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# ========== CHROMA CONFIGURATION ==========
# Name of the ChromaDB collection (you can create multiple collections if needed)
CHROMA_COLLECTION_NAME = "rag_documents"

# Embedding model to use (OpenAI or HuggingFace)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ========== ENVIRONMENT VARIABLES ==========
# Loaded securely from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ========== CHUNKING PARAMETERS ==========
# Customize how documents will be split into smaller parts
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 50      # Overlap between chunks to retain context

# ========== RETRIEVER CONFIG ==========
# Number of documents to fetch from each retriever
TOP_K_VECTOR = 2
TOP_K_KEYWORD = 3

# ========== DEBUGGING ==========
# Enable verbose logging for development
DEBUG = True

# Force re-indexing on startup (set to False in production or if index is stable)
FORCE_RE_INDEX = False