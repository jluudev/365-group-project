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
@router.get("/find_heroes/{dungeon_id}")
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
@router.post("/attack_hero/{monster_id}")
def attack_hero(monster_id: int):
    return {
        "success": "boolean"
    }

# Die - /monster/die/{monster_id} (GET)
@router.get("/die/{monster_id}")
def die(monster_id: int):
    return {
        "success": "boolean"
    }