import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv
import sqlalchemy


# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()

## SUPABASE SET UP  
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None

## Postgres

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())
metadata_obj = sqlalchemy.MetaData()

movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)
characters = sqlalchemy.Table("characters", metadata_obj, autoload_with=engine)
lines = sqlalchemy.Table("lines", metadata_obj, autoload_with=engine)
conversations = sqlalchemy.Table("conversations", metadata_obj, autoload_with=engine)

