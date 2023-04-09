from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    character = (db.characters[id] or None)

    if character is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    name = character["name"]
    movie_id = character["movie_id"]
    movie = db.movies[movie_id]["movie_title"]
    gender = character["gender"]

    # top conversation
    other_characters = {}

    conversations = db.conversations[movie_id]
    lines = db.lines[movie_id]
    # print(lines)

    for convo in conversations:
        if convo["character1_id"] == id:
            char = convo["character2_id"] # get id for 2nd character
            num_lines = lines[convo["conversation_id"]]
            total_lines = num_lines[id] + num_lines[char]
            if char not in other_characters:
                other_characters[char] = 0
            other_characters[char] += total_lines
        if convo["character2_id"] == id:
            char = convo["character1_id"] # get id for 2nd character
            num_lines = lines[convo["conversation_id"]]
            total_lines = num_lines[id] + num_lines[char]
            if char not in other_characters:
                other_characters[char] = 0
            other_characters[char] += total_lines

    top_conversation = []
    for other_id in other_characters:
        other_char = db.characters[other_id]
        info = {
                "character_id":other_id,
                "character":other_char["name"],
                "gender":other_char["gender"],
                "number_of_lines_together":other_characters[other_id]
              }
        top_conversation.append(info)
    sorted_convos = sorted(top_conversation, key=lambda x: (x["number_of_lines_together"], x["character"], x["character_id"]), reverse=True)

    json = {
      "character_id": id,
      "character": name,
      "movie": movie,
      "gender": gender,
      "top_characters": sorted_convos
      }

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    # sort characters by their name
    

    json = None
    return json
