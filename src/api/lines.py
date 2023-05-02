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
        lines_txt = "select lines.line_id, lines.conversation_id, lines.movie_id, c1.name as character1_name, c2.name as character2_name\
                    from lines\
                    join conversations as conv on lines.conversation_id = conv.conversation_id\
                    join characters as c1 on c1.character_id = conv.character1_id\
                    join characters as c2 on c2.character_id = conv.character2_id\
                    order by line_id asc \
                    limit :limit offset :offset"
        order_by = db.lines.c.line_id
    elif sort == line_sort_options.movie_id:
        lines_txt = "select lines.line_id, lines.conversation_id, lines.movie_id, c1.name as character1_name, c2.name as character2_name\
                    from lines\
                    join conversations as conv on lines.conversation_id = conv.conversation_id\
                    join characters as c1 on c1.character_id = conv.character1_id\
                    join characters as c2 on c2.character_id = conv.character2_id\
                    order by movie_id asc, line_id asc"
        order_by = db.lines.c.movie_id
    elif sort == line_sort_options.conversation_id:
        lines_txt = "select lines.line_id, lines.conversation_id, lines.movie_id, c1.name as character1_name, c2.name as character2_name\
                    from lines\
                    join conversations as conv on lines.conversation_id = conv.conversation_id\
                    join characters as c1 on c1.character_id = conv.character1_id\
                    join characters as c2 on c2.character_id = conv.character2_id\
                    order by conversation_id desc, line_id asc"
        order_by = sqlalchemy.desc(db.lines.c.conversation_id)
    else:
        assert False

    c1 = db.characters.alias("character1_name")
    c2 = db.characters.alias("character2_name")

    stmt = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.conversation_id,
            db.lines.c.movie_id,
            c1.c.name,
            c2.c.name
        )
        .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        .join(c1, c1.c.character_id == db.conversations.c.character1_id)
        .join(c2, c2.c.character_id == db.conversations.c.character2_id)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.lines.c.line_id)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            print(row)
            # json.append(
            #     {
            #         "movie_id": row.movie_id,
            #         "movie_title": row.title,
            #         "year": row.year,
            #         "imdb_rating": row.imdb_rating,
            #         "imdb_votes": row.imdb_votes,
            #     }
            # )

    return json
        
    
    

    # return None
    # lines = []

    # for line_id in db.lines:
    #     line = db.lines[line_id]
        
    #     if movie_id is not None and movie_id != line.movie_id:
    #         continue
    #     if conversation_id is not None and conversation_id != line.conv_id:
    #         continue

    #     characters = []
    #     characters.append(db.conversations[line.conv_id].c1_id)
    #     characters.append(db.conversations[line.conv_id].c2_id)
    #     sort_char_id = sorted(characters)

    #     result = {
    #         "line_id": line_id,
    #         "conversation_id": line.conv_id,
    #         "movie_id": line.movie_id,
    #         "character1_name": db.characters[sort_char_id[0]].name,
    #         "character2_name": db.characters[sort_char_id[1]].name,
    #     }

    #     lines.append(result)

    # if sort == line_sort_options.line_id:
    #     newlines = sorted(lines, key=lambda d: d['line_id']) 
    # elif sort == line_sort_options.movie_id:
    #     newlines = sorted(lines, key=lambda d: d['movie_id'])
    # elif sort == line_sort_options.conversation_id:
    #     newlines = sorted(lines, key=lambda d: d['conversation_id'], reverse=True)

    # return newlines[offset: offset + limit]


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