import os
from supabase import create_client, Client
from config import Config

def get_supabase_client() -> Client:
    url: str = Config.SUPABASE_URL
    key: str = Config.SUPABASE_KEY
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
    return create_client(url, key)

supabase: Client = get_supabase_client()
