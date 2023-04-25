from fastapi import APIRouter
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.datatypes import Conversation, Line


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

    # get id from last conversation added
    conv_id = int(db.conversations_ls[-1]["conversation_id"])
    
    new_conv_id = conv_id + 1

    # create new conversation; should we check data type?? yess
    new_conv = Conversation(
        db.try_parse(int, new_conv_id), 
        db.try_parse(int, conversation.character_1_id), 
        db.try_parse(int, conversation.character_2_id), 
        db.try_parse(int, movie_id), 
        len(conversation.lines),
        []
    )

    # add to conversations dictionary
    db.conversations[new_conv_id] = new_conv

    db.conversations_ls.append(
        {
            "conversation_id": db.conversations[new_conv_id].id,
            "character1_id": db.conversations[new_conv_id].c1_id,
            "character2_id": db.conversations[new_conv_id].c2_id,
            "movie_id": db.conversations[new_conv_id].movie_id
        })

    # get id from last line added
    ln_id = int(db.lines_ls[-1]["line_id"])
    new_ln_id = ln_id + 1

    line_sort = 1

    for ln in conversation.lines:
        new_ln = Line(
            db.try_parse(int, new_ln_id), 
            db.try_parse(int, ln.character_id), 
            db.try_parse(int, movie_id), 
            db.try_parse(int, new_conv_id), 
            db.try_parse(int, line_sort), 
            ln.line_text
        )

        # update conversation line_ids
        db.conversations[new_conv_id].line_ids.append(new_ln_id)

        # update lines dictionary
        db.lines[new_ln_id] = new_ln

        # update vars for next line
        new_ln_id += 1
        line_sort += 1
        
        db.lines_ls.append(
            {
                "line_id": new_ln.id,
                "character_id": new_ln.c_id,
                "movie_id": new_ln.movie_id,
                "conversation_id": new_ln.conv_id,
                "line_sort": new_ln.line_sort,
                "line_text": new_ln.line_text
            })


    ## add to lists (will be written into the files)
    
    
    db.upload_new_conversation()
    db.upload_new_line()

# adding a conversation that already exists? 
    
