from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/hero",
    tags=["hero"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Remove Dead Heroes - /guild/remove_heroes/{guild_id} (POST)
def remove_heroes(guild_id: int):
    return {
        "success": "boolean"
    }

# Check XP - /hero/check_xp/{hero_id} (POST)
def check_xp(hero_id: int):
    return {
        "xp": "number"
    }

# Raise Level - /hero/raise_level/{hero_id} (POST)
def raise_level(hero_id: int):
    return {
        "success": "boolean"
    }

# View Pending Requests - /hero/view_pending_requests/{hero_id} (GET)
def view_pending_requests(hero_id: int):
    return [
        {
            "guild_name":"string",
            "rank":"number",
            "gold":"number" 
        }
    ]

# Accept Request - /hero/accept_request/{hero_id}/{guild_id} (POST)
def accept_request(guild_id: int):
    return {
        "success": "boolean"
    }

# Attack Monster - /hero/attack_monster/{hero_id}/ (POST)
def attack_monster(hero_id: int):
    return {
        "success": "boolean"
    }

# Check Health - /hero/check_health/{hero_id}/ (GET)
def check_health(hero_id: int):
    return {
        "health": "number"
    }

# Run Away - /hero/run_away/{hero_id}/ (POST)
def run_away(hero_id: int):
    return {
        "success": "boolean"
    }

# Die - /hero/die/{hero_id}/ (POST)
def die(hero_id: int):
    return {
        "success": "boolean"
    }