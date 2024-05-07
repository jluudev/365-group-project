from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/hero",
    tags=["hero"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Check XP - /hero/check_xp/{hero_id} (POST)
@router.post("/check_xp/{hero_id}")
def check_xp():
    return {
        "xp": "number"
    }

# Raise Level - /hero/raise_level/{hero_id} (POST)
@router.post("/raise_level/{hero_id}")
def raise_level():
    return {
        "success": "boolean"
    }

# View Pending Requests - /hero/view_pending_requests/{hero_id} (GET)
@router.get("/view_pending_requests/{hero_id}")
def view_pending_requests(hero_id: int):
    requests = []
    with db.engine.begin() as connection:
        recruit = connection.execute(sqlalchemy.text
        ("""SELECT name, gold 
        FROM recruitment 
        JOIN guild ON recruitment.guild_id = guild.id 
        WHERE recruitment.hero_id = :id"""), [{"id": hero_id}])

        for request in recruit:
            requests.append({
                "guild_name": request.name,
                "gold": request.gold
            })

    return requests

# Accept Request - /hero/accept_request/{hero_id} (POST)
@router.post("/accept_request/{hero_id}")
def accept_request(hero_id: int, guild_name: str):
    sql_to_execute = sqlalchemy.text("""
    WITH guild_info AS (
        SELECT g.id AS guild_id, g.player_capacity
        FROM guild g
        WHERE g.name = :guild_name
        FOR UPDATE
    ),
    current_hero_count AS (
        SELECT COUNT(*) AS current_heroes
        FROM hero h
        WHERE h.guild_id IN (SELECT guild_id FROM guild_info)
    ),
    update_hero AS (
        UPDATE hero
        SET guild_id = (SELECT guild_id FROM guild_info)
        WHERE id = :hero_id AND guild_id IS NULL AND
              (SELECT current_heroes FROM current_hero_count) < (SELECT player_capacity FROM guild_info)
        RETURNING guild_id
    )
    UPDATE recruitment
    SET status = 'accepted', response_date = now()
    WHERE hero_id = :hero_id AND guild_id IN (SELECT guild_id FROM update_hero)
    RETURNING hero_id;
    """)

    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"guild_name": guild_name, "hero_id": hero_id})
        hero_updated = result.fetchone()
        if hero_updated:
            return {"success": True}
        else:
            raise HTTPException(status_code=400, detail="Request not found or hero already in a guild or guild is full")

# Attack Monster - /hero/attack_monster/{hero_id}/ (POST)
@router.post("/attack_monster/{hero_id}")
def attack_monster(monster_id: int):
    return {
        "success": "boolean"
    }

# Check Health - /hero/check_health/{hero_id}/ (GET)
@router.get("/check_health/{hero_id}")
def check_health():
    return {
        "health": "number"
    }

# Run Away - /hero/run_away/{hero_id}/ (POST)
@router.post("/run_away/{hero_id}")
def run_away():
    return {
        "success": "boolean"
    }

# Die - /hero/die/{hero_id}/ (POST)
@router.post("/die/{hero_id}")
def die():
    return {
        "success": "boolean"
    }

# Find Monsters - /hero/find_monsters/{dungeon_id}/ (GET)
@router.get("/find_monsters/{dungeon_id}")
def find_monsters():
    return [
        {
            "id":"number",
            "name" : "string",
            "level": "number",
            "power": "number",
        }
    ]