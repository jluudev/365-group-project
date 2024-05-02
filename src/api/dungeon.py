from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

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

class Hero(BaseModel):
    hero_name: str

# Create Dungeon - /dungeon/create_dungeon/{world_id} (POST)
@router.post("/create_dungeon/{world_id}")
def create_dungeon(dungeon: Dungeon):
    return {
        "success": "boolean"
    }

# Create Monster - /dungeon/create_monster/{dungeon_id} (POST)
@router.post("/create_monster/{dungeon_id}")
def create_monster(monsters: list[Monster]):
    return {
        "success": "boolean"
    }

# Collect Bounty - /dungeon/collect_bounty/{guild_id} (POST)
@router.post("/collect_bounty/{guild_id}")
def collect_bounty(guild_id: int):
    return {
        "gold": "number"
    }

# Assess Damage - /dungeon/assess_damage/{dungeon_id} (GET)
@router.get("/assess_damage/{dungeon_id}")
def assess_damage(dungeon_id: int):
    return [
        {
            "hero_name": "string",
            "level": "number",
            "power": "number",
            "age": "number",
        }
    ]
