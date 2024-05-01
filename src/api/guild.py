from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/guild",
    tags=["guild"],
    dependencies=[Depends(auth.get_api_key)],
)

# Endpoint
# Recruit Hero - /guild/recruit_hero/{hero_id}/ (POST)
@router.post("/recruit_hero/{hero_id}")
def recruit_hero(hero_id: int):
    return {
        "success": "boolean"
    }

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