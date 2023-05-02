from fastapi import APIRouter
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.datatypes import Conversation, Line
import sqlalchemy


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    try:
        last_conv_txt = """
        SELECT conversation_id 
        FROM conversations 
        ORDER BY conversation_id DESC 
        LIMIT 1
        """

        last_line_txt = """
        SELECT line_id 
        FROM lines 
        ORDER BY line_id DESC 
        LIMIT 1
        """

        with db.engine.begin() as conn:
            # Add new conversation
            conv_id = conn.execute(
                sqlalchemy.text(last_conv_txt)
            )

            for id in conv_id:
                new_conv_id = id.conversation_id + 1

            new_conv_txt = """
            INSERT INTO conversations (conversation_id, character1_id, character2_id, movie_id) 
            VALUES (:conv_id, :c1, :c2, :movie_id)
            """

            conn.execute(
                sqlalchemy.text(new_conv_txt),
                [{"conv_id": new_conv_id, 
                "c1": conversation.character_1_id, 
                "c2": conversation.character_2_id, 
                "movie_id": movie_id,
                }]
            )

            # Add new lines
            line_id = conn.execute(
                sqlalchemy.text(last_line_txt)
            )

            for id in line_id:
                new_line_id = id.line_id + 1

            line_sort = 1

            for line in conversation.lines:
                new_line_txt = """
                INSERT INTO lines (line_id, character_id ,movie_id, conversation_id, line_sort, line_text) 
                VALUES (:line_id, :character_id, :movie_id, :conversation_id, :line_sort, :line_text)
                """

                conn.execute(
                sqlalchemy.text(new_line_txt),
                    [{"line_id": new_line_id, 
                    "character_id": line.character_id,
                    "movie_id": movie_id,
                    "conversation_id": new_conv_id,
                    "line_sort": line_sort,
                    "line_text": line.line_text
                    }]
                )

                new_line_id += 1
                line_sort += 1

    except Exception as error:
        print(f"Error returned: <<<{error}>>>")
