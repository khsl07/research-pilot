import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    """Application settings and API configuration."""
    
    # Paths
    PROJECT_ROOT: Path = ROOT_DIR
    DATA_DIR: Path = ROOT_DIR / "data"
    CHROMA_DIR: Path = DATA_DIR / "chromadb"
    EXPORTS_DIR: Path = DATA_DIR / "exports"

    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")

    # LLM Settings
    DEFAULT_MODEL: str = os.getenv("RESEARCH_MODEL", "gemini-2.5-flash")
    DEFAULT_TEMPERATURE: float = 0.2
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

    # Vector store settings
    CHROMA_COLLECTION: str = "research_pilot_knowledge"
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 6

    @classmethod
    def ensure_directories(cls):
        """Ensure necessary storage directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
