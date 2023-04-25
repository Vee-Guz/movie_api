import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_logs.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_logs.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE


def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None


with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = {
        try_parse(int, row["movie_id"]): Movie(
            try_parse(int, row["movie_id"]),
            row["title"] or None,
            row["year"] or None,
            try_parse(float, row["imdb_rating"]),
            try_parse(int, row["imdb_votes"]),
            row["raw_script_url"] or None,
        )
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        char = Character(
            try_parse(int, row["character_id"]),
            row["name"] or None,
            try_parse(int, row["movie_id"]),
            row["gender"] or None,
            try_parse(int, row["age"]),
            0,
        )
        characters[char.id] = char


## Conversation -- read from dictionary
conversation_csv = (
    supabase.storage.from_("movie-api")
    .download("conversations.csv")
    .decode("utf-8")
)

conversations = {}
conversations_ls = []
for row in csv.DictReader(io.StringIO(conversation_csv), skipinitialspace=True):
    conv = Conversation(
        try_parse(int, row["conversation_id"]),
        try_parse(int, row["character1_id"]),
        try_parse(int, row["character2_id"]),
        try_parse(int, row["movie_id"]),
        0,
        []
    )
    conversations[conv.id] = conv
    conversations_ls.append(row)

def upload_new_conversation():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=[
        "conversation_id", 
        "character1_id", 
        "character2_id", 
        "movie_id", 
        "num_lines", 
        "line_ids"
        ]
    )
    csv_writer.writeheader()
    csv_writer.writerows(conversations_ls)
    supabase.storage.from_("movie-api").upload(
        "conversations.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )



## Lines -- read from dictionary

lines_csv = (
    supabase.storage.from_("movie-api")
    .download("lines.csv")
    .decode("utf-8")
)


lines = {}
lines_ls = []
for row in csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True):
    line = Line(
        try_parse(int, row["line_id"]),
        try_parse(int, row["character_id"]),
        try_parse(int, row["movie_id"]),
        try_parse(int, row["conversation_id"]),
        try_parse(int, row["line_sort"]),
        row["line_text"],
    )
    lines[line.id] = line
    c = characters.get(line.c_id)
    if c:
        c.num_lines += 1

    conv = conversations.get(line.conv_id)
    if conv:
        conv.num_lines += 1
        conv.line_ids.append(line.id)

    lines_ls.append(row)

# add completed conversations to csv file
# for conv in conversations:
#     result = {
#         "conversation_id": conv.id,
#         "character1_id": conv.c1_id,
#         "character2_id": conv.c2_id,
#         "movie_id": conv.movie_id,
#         "num_lines": conv.num_lines,
#         "line_ids": conv.line_ids
#         }
#     conversations_ls.append(result)
    

def upload_new_line():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["line_id", "character_id", "movie_id", "conversation_id", "line_sort", "line_text"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(lines_ls)
    supabase.storage.from_("movie-api").upload(
        "lines.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )