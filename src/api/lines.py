from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query

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

# class line_sort_options(str, Enum):
#     line_id = "line_id"
#     movie_id = "movie_id"
#     conversation_id = "conversation_id"


@router.get("/lines/", tags=["lines"])
def list_lines(
    movie_id: int = None,
    conversation_id: int = None,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    # sort: line_sort_options = line_sort_options.line_id,
):
    """
    This endpoint returns a list of all the conversations. For each conversation it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `conversation_id`: the conversation id the line belongs to
    * `movie_id`: The movie id the conversation is in.
    * `character1_name`: The name of the 1st character that is a part of the conversation.
    * `character2_name`: The name of the 2st character that is a part of the conversation.

    # You can also sort the results by using the `sort` query parameter:
    # * `line_id` - Sort by line_id, highest to lowest.
    # * 'movie_id' - Sort by movie_id, highest to lowest.
    # * 'conversation_id' - Sort by conversation_id, highest to lowest.


    You can filter for lines that belong to the movies by using the query parameter `movie_id` and 
    lines that belong to a certain conversation by using the query parameter 'conversation_id'.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    lines = []

    for line_id in db.lines:
        line = db.lines[line_id]
        
        if movie_id is not None and movie_id != line.movie_id:
            continue
        if conversation_id is not None and conversation_id != line.conv_id:
            continue

        characters = []
        characters.append(db.conversations[line.conv_id].c1_id)
        characters.append(db.conversations[line.conv_id].c2_id)
        sort_char_id = sorted(characters)

        result = {
            "line_id": line_id,
            "conversation_id": line.conv_id,
            "movie_id": line.movie_id,
            "character1_name": db.characters[sort_char_id[0]].name,
            "character2_name": db.characters[sort_char_id[1]].name,
        }

        lines.append(result)

    return lines[offset: offset + limit]


