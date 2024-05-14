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
    sql_to_execute = """
    INSERT INTO guild (name, max_capacity, gold, world_id)
    VALUES (:name, :max_capacity, :gold, :world_id);
    """
    with db.engine.begin() as connection:
        connection.execute(sql_to_execute, {
            "name": guild.guild_name,
            "max_capacity": guild.max_capacity,
            "gold": guild.gold,
            "world_id": world_id
        })

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
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT name, power, health, level
            FROM hero
            WHERE guild_id = :guild_id AND dungeon_id IS NULL
            """), {"guild_id": guild_id}
        )
        heroes = [
            {"hero_name": row[0], "power": row[1], "health": row[2], "level": row[3]} 
            for row in result.fetchall()
        ]
    return heroes

# Remove Dead Heroes - /guild/remove_heroes/{guild_id} (POST)
@router.post("/remove_heroes/{guild_id}")
def remove_heroes(guild_id: int, heroes: list[Hero]):
    hero_names = [hero.hero_name for hero in heroes]
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            DELETE FROM hero
            WHERE name = ANY(:hero_names) AND guild_id = :guild_id AND health <= 0
            """), {"hero_names": hero_names, "guild_id": guild_id}
        )
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "No dead heroes found"}

# Send Party - /guild/send_party/{guild_id} (POST)
@router.post("/send_party/{guild_id}")
def send_party(guild_id: int, party: list[Hero], dungeon_name: str):
    # Check if the guild exists
    guild_query = sqlalchemy.text("SELECT * FROM guild WHERE id = :guild_id FOR UPDATE")
    with db.engine.begin() as connection:
        guild = connection.execute(guild_query, {"guild_id": guild_id}).fetchone()
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        
        # Update hero dungeon_id
        for hero in party:
            update_hero = sqlalchemy.text("""
            UPDATE hero
            SET dungeon_id = (SELECT id FROM dungeon WHERE name = :dungeon_name AND status = 'open')
            WHERE name = :hero_name AND guild_id = :guild_id
            """)
            result = connection.execute(update_hero, {"hero_name": hero.hero_name, "guild_id": guild_id, "dungeon_name": dungeon_name})
            
            if result.rowcount > 0:
                connection.execute(sqlalchemy.text("""
                                                UPDATE dungeon
                                                SET status = 'closed'
                                                WHERE name = :dungeon_name"""),
                                                {"dungeon_name": dungeon_name})
                return {"success": True}
            else:
                return {"success": False, "message": "Hero not found or already in a dungeon"}

