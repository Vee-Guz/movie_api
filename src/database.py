import csv

# TODO: You will want to replace all of the code below. It is just to show you
# an example of reading the CSV files where you will get the data to complete
# the assignment.

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        (movie_id,title,year,imdb_rating,imdb_votes,raw_script_url) = row.items()
        # make movie_id the key
        movies[int(movie_id[1])] = {
                                "movie_title":title[1],
                                "year":year[1],
                                "imdb_rating":float(imdb_rating[1]),
                                "imdb_votes":int(imdb_votes[1]),
                                "raw_script_url":raw_script_url[1]
                            }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        (character_id, name, movie_id, gender, age) = row.items() # unpack row tuple
        characters[int(character_id[1])] = {
                                            "name": name[1],
                                            "movie_id": int(movie_id[1]),
                                            "gender": (gender[1] or None),
                                            "age": age[1]
                                        }
    # sort characters by their name
    # characters = sorted(characters.items(), key=lambda x: x[1]["name"])
    

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    # conversation_id,character1_id,character2_id,movie_id
    # need how many line a character shares with another character -- identify coversation_id, use coversation id to look at lines, count total number of lines spoken for each coversation
    # for every coversation
    #   if character id 1 does not exists, then create in dict
    # {"movie_id": {"5015": [coversation_id1, ...], "5043"}}
    
    conversations = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        (conversation_id,character1_id,character2_id,movie_id) = row.items()
        info = {
            "conversation_id": int(conversation_id[1]), 
            "character1_id": int(character1_id[1]), 
            "character2_id": int(character2_id[1])
            }
        movie = int(movie_id[1])
        if movie not in conversations:
            conversations[movie] = []
        conversations[movie].append(info)
        
    # conversations = [
    #     {k: v for k, v in row.items()}
    #     for row in csv.DictReader(csv_file, skipinitialspace=True)
    # ]


with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    # line_id,character_id,movie_id,conversation_id,line_sort,line_text
    lines = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        (line_id,character_id,movie_id,conversation_id,line_sort,line_text) = row.items()
        movie = int(movie_id[1])
        convo = int(conversation_id[1])
        char = int(character_id[1])
        if movie not in lines:
            lines[movie] = {}
        if convo not in lines[movie]:
            lines[movie][convo] = {}
        if char not in lines[movie][convo]:
            lines[movie][convo][char] = 0
        lines[movie][convo][char] += 1
    
    # lines = [
    #     {k: v for k, v in row.items()}
    #     for row in csv.DictReader(csv_file, skipinitialspace=True)
    # ]
