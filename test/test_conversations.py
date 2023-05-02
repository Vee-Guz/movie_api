from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_add_conversation():
    ## add a conversation
    response = client.post(
        "/movies/240/conversations/",
        json={
            "character_1_id": 3642,
            "character_2_id": 3640,
            "lines": [
                {
                "character_id": 3642,
                "line_text": "hello"
                },
                {
                "character_id": 3640,
                "line_text": "hello. how are you?"
                },
                {
                "character_id": 3642,
                "line_text": "i am good. how are you?"
                },
                {
                "character_id": 3640,
                "line_text": "i am doing great. thanks for asking!"
                },
            {
                "character_id": 3642,
                "line_text": "how was work?"
                },
                {
                "character_id": 3640,
                "line_text": "work was good. a lot of work. i am so tired."
                },
            {
                "character_id": 3642,
                "line_text": "make sure to take some rest!"
                },
                {
                "character_id": 3640,
                "line_text": "i will. i have some plans to relax at the end of the week."
                }
            ]
        })
    assert response.status_code == 200


def test_lines_recently_added():
    # verify that the latest lines added are for the movie above and that 
    # the character_names match
    response = client.get("lines/?sort=conversation_id")
    assert response.status_code == 200

    assert response.json()[0]["character1_name"] == "JIM"
    assert response.json()[0]["character2_name"] == "HEATHER"
    assert response.json()[0]["movie_id"] == 240

