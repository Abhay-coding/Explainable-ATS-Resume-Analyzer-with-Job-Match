import os 
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load from both root and backend directories
    root_dir = Path(__file__).parent.parent.parent  # project root
    backend_dir = Path(__file__).parent.parent  # backend dir
    load_dotenv(root_dir / '.env')
    load_dotenv(backend_dir / '.env')
except ImportError:
    pass

#metadata
APP_TITLE='ATS Resume Analyzer API'
APP_VERSION='1.0.0'
APP_DESCRIPTION='AI-powered resume analysis and job matching using NLP and ML'


ALLOWED_ORIGINS = [
    "https://explainable-ats-resume-analyzer-with-job-match-ecrwukdgcx8ikko.streamlit.app/"
]


MAX_FILE_SIZE_MB=5
MAX_FILE_SIZE_BYTES=MAX_FILE_SIZE_MB*1024*1024

SUPPORTED_MIME_TYPES = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
}

SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx"}

SPACY_MODEL_PRIMARY = os.getenv("SPACY_MODEL_PRIMARY", "en_core_web_md")      # better accuracy
SPACY_MODEL_SECONDARY = "en_core_web_sm"

SENTENCE_TRANSFORMER_MODEL = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL",
    "all-MiniLM-L6-v2"
)

# score component weights (should sum to 100)
SCORE_WEIGHTS = {
    "formatting": 20,
    "keywords": 25,
    "content": 25,
    "skill_validation": 15,
    "ats_compatibility": 15,
}

JD_KEYWORD_WEIGHT = 0.6
JD_SEMANTIC_WEIGHT = 0.4

SUPABASE_URL = os.getenv("SUPABASE_URL","")
SUPABASE_KEY = os.getenv("SUPABASE_KEY","")              # service role (DB writes)
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY","")    # public anon (frontend)
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET","")# verify tokens

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")