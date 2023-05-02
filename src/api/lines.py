from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
import sqlalchemy

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
    line_txt = "select line_id, movies.title as title, conversation_id, characters.name as name, line_text from lines join movies on movies.movie_id = lines.movie_id join characters on characters.character_id = lines.character_id where lines.line_id = :line_id"

    result = None

    with db.engine.connect() as conn:
        line = conn.execute(
            sqlalchemy.text(line_txt),
            [{"line_id": line_id}]
        )

        for l in line:
            result = {
                "line_id": l.line_id,
                "movie_title": l.title,
                "conversation_id": l.conversation_id,
                "character": l.name,
                "line_text": l.line_text
            }

        if result is None:
            raise HTTPException(status_code=404, detail="line not found.")
        
        return result

class line_sort_options(str, Enum):
    line_id = "line_id"
    movie_id = "movie_id"
    conversation_id = "conversation_id"


@router.get("/lines/", tags=["lines"])
def list_lines(
    movie_id: int = None,
    conversation_id: int = None,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: line_sort_options = line_sort_options.line_id,
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
    # * `line_id` - Sort by line_id, lowest to highest.
    # * 'movie_id' - Sort by movie_id, lowest to highest.
    # * 'conversation_id' - Sort by conversation_id, highest to lowest.


    You can filter for lines that belong to the movies by using the query parameter `movie_id` and 
    lines that belong to a certain conversation by using the query parameter 'conversation_id'.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    if sort == line_sort_options.line_id:
        order_by = db.lines.c.line_id
    elif sort == line_sort_options.movie_id:
        order_by = db.lines.c.movie_id
    elif sort == line_sort_options.conversation_id:
        order_by = sqlalchemy.desc(db.lines.c.conversation_id)
    else:
        assert False

    c1 = db.characters.alias("c1")
    c2 = db.characters.alias("c2")

    stmt = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.conversation_id,
            db.lines.c.movie_id,
            c1.c.name.label("character1_name"),
            c2.c.name.label("character2_name")
        )
        .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        .join(c1, c1.c.character_id == db.conversations.c.character1_id)
        .join(c2, c2.c.character_id == db.conversations.c.character2_id)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.lines.c.line_id)
    )

    if movie_id is not None:
        stmt = stmt.where(db.lines.c.movie_id == movie_id)

    if conversation_id is not None:
        stmt = stmt.where(db.conversations.c.conversation_id == conversation_id)


    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "line_id": row.line_id,
                    "conversation_id": row.conversation_id,
                    "movie_id": row.movie_id,
                    "character1_name": row.character1_name,
                    "character2_name": row.character2_name,

                }
            )

    return json
    

@router.get("/line-sort/{conv_id}", tags=["lines"])
def sort_conv_lines(conv_id: int):
    """
    This endpoint returns all the line_text in a conversation in the order spoken. For each line it returns:
    * `line_id`: the internal id of the line.
    * `conversation_id`: the conversation id representing the conversation where the line is spoken.
    * `movie_id`: the movie_id represents the movie in which the line is spoken.
    * `line_sort`: The order number the line is spoken.
    * `character`: character name that says the line.
    * `line_text`: the line text.
    """

    conv_txt = "select line_id, conversation_id, movies.movie_id as movie_id, line_sort, characters.name as name, line_text from lines join movies on movies.movie_id = lines.movie_id join characters on characters.character_id = lines.character_id where lines.conversation_id = :id order by line_sort ASC"

    result = None

    with db.engine.connect() as conn:
        conv = conn.execute(
            sqlalchemy.text(conv_txt),
            [{"id": conv_id}]
        )

        result = (
            {
                "line_id": c.line_id,
                "conversation_id": c.conversation_id,
                "movie_id":  c.movie_id,
                "line_sort": c.line_sort,
                "character": c.name,
                "line_text": c.line_text
            }
            for c in conv
        )

        if result is None:
            raise HTTPException(status_code=404, detail="conversation not found.")
        
        return result