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
def collect_bounty():
    return {
        "gold": "number"
    }

# Assess Damage - /dungeon/assess_damage/{dungeon_id} (GET)
@router.get("/assess_damage/{dungeon_id}")
def assess_damage():
    return [
        {
            "hero_name": "string",
            "level": "number",
            "power": "number",
            "age": "number",
        }
    ]
