from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/monster",
    tags=["monster"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Find Heroes - /monster/find_heroes/{dungeon_id}/ (GET)
def find_heroes(dungeon_id: int):
    return [
        {
            "id":"number",
            "name" : "string",
            "level": "number",
            "power": "number",
        }
    ]

# Attack Hero - /monster/attack_hero/{monster_id}/ (POST)
def attack_hero(monster_id: int):
    return {
        "success": "boolean"
    }

# Die - /monster/die/{monster_id} (GET)
def die(monster_id: int):
    return {
        "success": "boolean"
    }