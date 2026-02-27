from supabase_client import supabase
import os

def test_connection():
    try:
        print(f"Testing connection to: {os.getenv('SUPABASE_URL')}")
        
        # Try to fetch from 'users' table (even if empty) to verify API key
        response = supabase.table('users').select("*").limit(1).execute()
        
        print("Supabase connection verified! API key is valid.")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nTIP: Make sure you copied the 'anon' 'public' key from Supabase Settings -> API.")

if __name__ == "__main__":
    test_connection()
