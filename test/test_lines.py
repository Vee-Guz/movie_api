from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_lines():
    response = client.get("/lines/49")
    assert response.status_code == 200

    with open("test/lines/49.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get(
        "/lines?movie_id=11"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-movie_id=11.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_sort_filter_2():
    response = client.get(
        "/lines?movie_id=11&conversation_id=46"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-movie_id=11&conversation_id=46.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_sort_filter_3():
    response = client.get(
        "/lines?movie_id=11&limit=5&offset=1"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-movie_id=11&limit=5&offset=1.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_sort_filter_3():
    response = client.get(
        "/lines?conversation_id=189&limit=5&offset=1&movie_id=0"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-conversation_id=189&limit=5&offset=1&movie_id=0.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/lines/400")
    assert response.status_code == 404