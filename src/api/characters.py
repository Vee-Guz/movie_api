from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy

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

    character_txt = "select c.character_id as id, c.name as name, movies.title as movie, c.gender as gender from characters as c join movies on movies.movie_id = c.movie_id where c.character_id = :id"
    top_conv_text = "select c.character_id as id, c.name as name, c.gender as gender, count(*) num_lines_together from characters as c join conversations as conv on conv.character1_id = c.character_id or conv.character2_id = c.character_id join lines on conv.conversation_id = lines.conversation_id where (conv.character1_id = :id or conv.character2_id = :id) and c.character_id != :id group by c.character_id, c.name, c.gender order by num_lines_together desc"


    with db.engine.connect() as conn:
        character = conn.execute(
            sqlalchemy.text(character_txt),
            [{"id": id}]
        )

        top_conv = conn.execute(
            sqlalchemy.text(top_conv_text),
            [{"id": id}]
        )

        result = None

        for char in character:
            result = {
                "character_id": char.id,
                "character": char.name,
                "movie": char.movie,
                "gender": char.gender,
                "top_conversations": (
                    {
                        "character_id": conv.id,
                        "character": conv.name,
                        "gender": conv.gender,
                        "number_of_lines_together": conv.num_lines_together,
                    }
                    for conv in top_conv
                ),
            }

        if result is None:
            raise HTTPException(status_code=404, detail="character not found.")
        
        return result
    

class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
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

    if sort == character_sort_options.character:
        txt = "SELECT c.character_id As id, name, movies.title as title, COUNT(*) num_lines FROM characters AS c JOIN movies ON c.movie_id = movies.movie_id JOIN lines ON c.character_id = lines.character_id WHERE name ILIKE :name GROUP BY c.character_id, movies.title ORDER BY name ASC, c.character_id ASC  LIMIT :limit OFFSET :offset"
    elif sort == character_sort_options.movie:
        txt = "SELECT c.character_id As id, name, movies.title as title, COUNT(*) num_lines FROM characters AS c JOIN movies ON c.movie_id = movies.movie_id JOIN lines ON c.character_id = lines.character_id WHERE name ILIKE :name GROUP BY c.character_id, movies.title ORDER BY title ASC LIMIT :limit OFFSET :offset"
    elif sort == character_sort_options.number_of_lines:
        txt = "SELECT c.character_id As id, name, movies.title as title, COUNT(*) num_lines FROM characters AS c JOIN movies ON c.movie_id = movies.movie_id JOIN lines ON c.character_id = lines.character_id WHERE name ILIKE :name GROUP BY c.character_id, movies.title ORDER BY num_lines DESC, title ASC LIMIT :limit OFFSET :offset"

    with db.engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(txt),
            [{"name": f"%{name}%", "limit": limit, "offset": offset}]
        )
        json = []
        for row in result:
            json.append(
                {
                    "character_id": row.id,
                    "character": row.name,
                    "movie": row.title,
                    "number_of_lines": row.num_lines,
                }
            )
    return json
