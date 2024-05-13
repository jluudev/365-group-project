from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/monster",
    tags=["monster"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Find Heroes - /monster/find_heroes/{dungeon_id}/ (GET)
@router.get("/find_heroes/{dungeon_id}")
def find_heroes():
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
def attack_hero(hero_id: int):
    return {
        "success": "boolean"
    }

# Die - /monster/die/{monster_id} (GET)
@router.get("/die/{monster_id}")
def die(monster_id: int):
    sql_delete_monster = """
    WITH deleted_targeting AS (
        DELETE FROM targeting
        WHERE monster_id = :monster_id
        RETURNING *
    ),
    deleted_monster AS (
        DELETE FROM monster
        WHERE id = :monster_id AND health = 0
        RETURNING *
    )
    SELECT * FROM deleted_monster;
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(sql_delete_monster), {"monster_id": monster_id})
        deleted_monster = result.fetchone()

    if deleted_monster:
        return {"success": True}
    else:
        return {"success": False, "message": "Monster is still alive or not found"}
