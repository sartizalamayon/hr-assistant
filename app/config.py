import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/hr_assist")
# Some hosts (Render, Heroku, etc.) hand out "postgres://" URLs, but SQLAlchemy
# requires the "postgresql://" scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")

COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "")
COHERE_EMBED_MODEL = "embed-english-v3.0"
EMBEDDING_DIM = 1024

# Chunking
CHUNK_SIZE_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150

# Retrieval / confidence
TOP_K_CHUNKS = 4
SIMILARITY_THRESHOLD = 0.35  # cosine similarity below this -> not confident enough

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
MAX_UPLOAD_MB = 20
