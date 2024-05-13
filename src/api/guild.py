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
    WHERE name = :hero_name AND guild_id IS NULL AND world_id = (SELECT world_id FROM guild WHERE id = :guild_id);
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
    # Check if the guild exists
    guild_query = sqlalchemy.text("SELECT * FROM guild WHERE id = :guild_id FOR UPDATE")
    with db.engine.connect() as connection:
        guild_result = connection.execute(guild_query, {"guild_id": guild_id})
        guild = guild_result.fetchone()
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found.")

        # Check if the dungeon exists and has available capacity
        dungeon_query = sqlalchemy.text("SELECT * FROM dungeon WHERE name = :dungeon_name FOR UPDATE")
        dungeon_result = connection.execute(dungeon_query, {"dungeon_name": dungeon_name})
        dungeon = dungeon_result.fetchone()
        if not dungeon:
            raise HTTPException(status_code=404, detail="Dungeon not found.")
        if dungeon["party_capacity"] < len(party):
            raise HTTPException(status_code=400, detail="Dungeon doesn't have enough capacity for the party.")

        # Update hero dungeon_id
        update_hero_query = sqlalchemy.text(
            "UPDATE hero SET dungeon_id = :dungeon_id WHERE id = ANY(:hero_ids)"
        )
        hero_ids = [hero.id for hero in party]
        connection.execute(
            update_hero_query,
            {"dungeon_id": dungeon["id"], "hero_ids": hero_ids}
        )

    return {"success": True}