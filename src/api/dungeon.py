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
    name: str
    level: int
    player_capacity: int
    monster_capacity: int

# Create Dungeon - /dungeon/create_dungeon/ (POST)
@router.post("/create_dungeon")
def create_dungeon(dungeon: Dungeon):
    return {
        "success": "boolean"
    }

# Create Monster - /dungeon/create_monster/ (POST)
@router.post("/create_monster")
def create_monster():
    return {
        "success": "boolean"
    }

# Send Party - /dungeon/send_party/{dungeon_id} (POST)
@router.post("/send_party/{dungeon_id}")
def send_party(dungeon_id: int):
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

# Find Monsters - /dungeon/find_monsters/{dungeon_id}/ (GET)
@router.get("/find_monsters/{dungeon_id}")
def find_monsters(dungeon_id: int):
    return [
        {
            "id":"number",
            "name" : "string",
            "level": "number",
            "power": "number",
        }
    ]
