from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/world",
    tags=["world"],
    dependencies=[Depends(auth.get_api_key)],
)

# Guild Model
class Guild(BaseModel):
    name: str
    capacity: int

# Endpoints

# Create Guild - /world/create_guild/ (POST)
def create_guild(guild: Guild):
    return {
        "success": True
    }

# View Heroes - /world/view_heroes/ (GET)
def view_heroes():
    return {
        "success": True
    }

# Get Quests - /world/get_quests/ (GET)
def get_quests():
    return [
            {
                "dungeon_name": "string",
                "level": "number",
            }
        ]

# Create Hero - /world/create_hero/ (POST)
def create_hero():
    return {
        "success": True
    }

# Age Hero - /world/age_hero/{hero_id} (POST)
def age_hero(hero_id: int):
    return {
        "success": True
    }
