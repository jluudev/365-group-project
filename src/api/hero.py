from fastapi import APIRouter, Depends
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
    
    """)
    try:
        with db.engine.begin() as connection:
            guild_id = connection.execute(sqlalchemy.text("SELECT guild.id FROM guild WHERE guild.name = :guild_name"), {"guild_name": guild_name}).scalar()
            guild_capacity = connection.execute(sqlalchemy.text("SELECT guild.player_capacity FROM guild WHERE guild.id = :guild_id"), {"guild_id": guild_id}).scalar()
            guild_num = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM hero WHERE hero.guild_id = :guild_id"), {"guild_id": guild_id}).scalar()
            if guild_capacity > guild_num:
                connection.execute(sqlalchemy.text("UPDATE hero SET guild_id = :guild_id WHERE hero.id = :hero_id"), {"guild_id": guild_id, "hero_id": hero_id})
                connection.execute(sqlalchemy.text("UPDATE recruitment SET (status, response_date) = ('accepted', now()) WHERE recruitment.hero_id = :hero_id AND recruitment.guild_id = :guild_id"), {"guild_id": guild_id, "hero_id": hero_id})
            else:
                raise Exception("Guild already full, rolling back.")
    except Exception as error:
        print(f"Error returned: <<<{error}>>>")

    return {
        "success": "true"
    }

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