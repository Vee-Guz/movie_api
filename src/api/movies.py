from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """

    if movie_id not in db.movies:
        raise HTTPException(status_code=404, detail="movie not found.")

    movie_info = db.movies[movie_id]
    print(movie_info)

    title = movie_info["movie_title"]

    lines = db.lines[movie_id]
    chars_lines = {}

    for conv in lines:
        for char_id in lines[conv]:
            if char_id not in chars_lines:
                chars_lines[char_id] = 0
            chars_lines[char_id] += lines[conv][char_id]

    sorted_lines = sorted(chars_lines.items(), key= lambda x : x[1], reverse=True)

    movie_conversations = []
    for i in sorted_lines:
        if len(movie_conversations) == 5:
            break

        character_id = i[0]
        char_info = db.characters[character_id]
        char_name = char_info["name"]
        num_lines = i[1]

        info = {"character_id": character_id,"character": char_name,"num_lines": num_lines}

        movie_conversations.append(info)

    json = {"movie_id": movie_id, "title": title, "top_characters": movie_conversations}

    return json


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    all_movies = []
    for movie_id in db.movies:
        movie = db.movies[movie_id]

        movie_title = movie["movie_title"]
        year = movie["year"]
        imdb_rating = movie["imdb_rating"]
        imdb_votes = movie["imdb_votes"]

        if name.lower() not in movie_title.lower():
            continue

        json = {
                "movie_id": movie_id, 
                "movie_title": movie_title, 
                "year": year,
                "imdb_rating": imdb_rating,
                "imdb_votes":imdb_votes
                }

        all_movies.append(json)

    if sort == movie_sort_options.movie_title:
        sorted_movies = sorted(all_movies, key=lambda x: x["movie_title"])
    elif sort == movie_sort_options.year:
        sorted_movies = sorted(all_movies, key=lambda x: x["year"])
    else:   # sort by rating
        sorted_movies = sorted(all_movies, key=lambda x: x["imdb_rating"], reverse=True)

    if len(sorted_movies) < limit:
        limit = len(sorted_movies)

    if offset > len(sorted_movies):
        offset = len(sorted_movies)


    result = []
    for i in range(offset, limit, 1):
        result.append(sorted_movies[i])

    return result
