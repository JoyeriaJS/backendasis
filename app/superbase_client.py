from app.supabase import create_client

SUPABASE_URL = "https://fqfsazuxquxvwnnokozr.supabase.co/rest/v1/"
SUPABASE_KEY = "0dtKfXQeTvuWgf3S"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

