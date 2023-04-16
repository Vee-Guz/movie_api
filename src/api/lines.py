from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_lines(line_id: int):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * `line_id`: the internal id of the line.
    * `movie_title`: The title of the movie the line is from.
    * `conversation_id`: the conversation id representing the conversation where the line is spoken.
    * `character`: character name that says the line.
    * `line_text`: the line text.

    """

    line = db.lines.get(line_id)
    if line:
        character = db.characters.get(line.c_id)
        movie_title = db.movies[line.movie_id].title
        result = {
    		"line_id": line_id,
    		"movie_title": movie_title,
    		"conversation_id": line.conv_id,
    		"character": character.name,
    		"line_text": line.line_text
    	}

        return result

    raise HTTPException(status_code=404, detail="line not found.")

# API 1
# One of the calls must reference the characters speaking the line by name.
# return all lines from a conversation in a movie in the order spoken

# /lines/{id} - return


# API 2
# return all the coversation_ids (in a list) of a movie

# API 3
# given the coversation_id return number of lines 