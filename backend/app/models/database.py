import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError('SUPABASE_URL과 SUPABASE_KEY를 backend/.env에 설정해주세요')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    return supabase
