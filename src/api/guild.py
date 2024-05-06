from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/guild",
    tags=["guild"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model
class Hero(BaseModel):
    hero_name: str

class Guild(BaseModel):
    guild_name: str
    max_capacity: int
    gold: int

# Endpoint

# Create Guild - /world/create_guild/{world_id} (POST)
@router.post("/create_guild/{world_id}")
def create_guild(world_id: int, guild: Guild):
    return {
        "success": True
    }

# Recruit Hero - /guild/recruit_hero/{guild_id} (POST)
@router.post("/recruit_hero/{guild_id}")
def recruit_hero(guild_id: int, hero: Hero):
    sql_to_execute = sqlalchemy.text("""
    INSERT INTO recruitment (hero_id, guild_id, status, request_date)
    SELECT id, :guild_id, 'pending', now() 
    FROM hero 
    WHERE name = :hero_name AND guild_id IS NULL;
    """)

    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {'hero_name': hero.hero_name, 'guild_id': guild_id})
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero not found or already in a guild"}

# Check Available Heroes - /guild/available_heroes/{guild_id} (GET)
@router.get("/available_heroes/{guild_id}")
def available_heroes(guild_id: int):
    return [
        {
            "hero_name": "string",
            "level": "number",
            "power": "number",
            "age": "number",
        }
    ]

# Remove Dead Heroes - /guild/remove_heroes/{guild_id} (POST)
@router.post("/remove_heroes/{guild_id}")
def remove_heroes(guild_id: int, heroes: list[Hero]):
    return {
        "success": "boolean"
    }

# Send Party - /guild/send_party/{guild_id} (POST)
@router.post("/send_party/{guild_id}")
def send_party(guild_id: int, party: list[Hero], dungeon_name: str):
    return {
        "success": "boolean"
    }