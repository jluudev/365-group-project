from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/dungeon",
    tags=["dungeon"],
    dependencies=[Depends(auth.get_api_key)],
)

# Endpoint

# Models
class Dungeon(BaseModel):
    dungeon_name: str
    dungeon_level: int
    player_capacity: int
    monster_capacity: int
    reward: int

class Monster(BaseModel):
    type: str
    health: int
    power: int
    level: int

class Hero(BaseModel):
    hero_name: str

# Create Dungeon - /dungeon/create_dungeon/{world_id} (POST)
@router.post("/create_dungeon/{world_id}")
def create_dungeon(world_id: int, dungeon: Dungeon):
    sql_to_execute = """
    INSERT INTO dungeon (name, level, player_capacity, monster_capacity, reward, world_id)
    VALUES (:name, :level, :player_capacity, :monster_capacity, :reward, :world_id);
    """
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "name": dungeon.dungeon_name,
            "level": dungeon.dungeon_level,
            "player_capacity": dungeon.player_capacity,
            "monster_capacity": dungeon.monster_capacity,
            "reward": dungeon.reward,
            "world_id": world_id
        })
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False}

# Create Monster - /dungeon/create_monster/{dungeon_id} (POST)
@router.post("/create_monster/{dungeon_id}")
def create_monster(dungeon_id: int, monsters: Monster):
    sql_to_execute = """
    INSERT INTO monster (type, health, dungeon_id, power, level)
    VALUES (:type, :health, :dungeon_id, :power, :level);
    """
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "type": monsters.type,
            "health": monsters.health,
            "dungeon_id": dungeon_id,
            "power": monsters.power,
            "level": monsters.level
        })

    return {
        "success": True
    }

# Collect Bounty - /dungeon/collect_bounty/{guild_id} (POST)
@router.post("/collect_bounty/{guild_id}")
def collect_bounty(guild_id: int, dungeon_id: int):
    # Only collect bounty if no monsters are alive (no monsters with that dungeon_id)
    sql_to_execute = sqlalchemy.text("""
    WITH monster_count AS (
    SELECT COUNT(*) AS count
    FROM monster
    WHERE dungeon_id = :dungeon_id AND health > 0
    )
    UPDATE guild
    SET gold = gold + (SELECT gold_reward FROM dungeon WHERE id = :dungeon_id)
    WHERE id = :guild_id
    AND (SELECT count FROM monster_count) = 0
    RETURNING gold;
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"dungeon_id": dungeon_id, "guild_id": guild_id})
        if result.rowcount > 0:
            # Return the amount of gold collected
            return {"gold": result.fetchone()[0]}
        else:
            return {"success": False, "message": "Failed to collect bounty"}

# Assess Damage - /dungeon/assess_damage/{dungeon_id} (GET)
@router.get("/assess_damage/{dungeon_id}")
def assess_damage(guild_id: int, dungeon_id: int):
    sql_to_execute = """
    SELECT name, level, power, health
    FROM hero
    WHERE guild_id = :guild_id AND dungeon_id = :dungeon_id AND health <= 0
    """
    with db.engine.begin() as connection:
        heroes = connection.execute(sqlalchemy.text(sql_to_execute), {"guild_id": guild_id, "dungeon_id": dungeon_id})

    returning_heroes = []
    for hero in heroes:
        returning_heroes.append(
            {
                "hero_name": hero.name,
                "level": hero.level,
                "power": hero.power,
                "health": hero.health
            }
        )
    return returning_heroes