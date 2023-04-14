from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

# API 1
# One of the calls must reference the characters speaking the line by name.
# return all lines from a conversation in a movie in the order spoken

# /lines/{id} - return


# API 2
# return all the coversation_ids (in a list) of a movie

# API 3
# given the coversation_id return number of lines 