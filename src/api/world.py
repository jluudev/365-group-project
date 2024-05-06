from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/world",
    tags=["world"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model
class Hero(BaseModel):
    hero_name: str
    classType: str
    level: int
    age: int


# Endpoints
# View Heroes - /world/view_heroes/{world_id} (GET)
@router.get("/view_heroes/{world_id}")
def view_heroes(world_id: int):

    heroes = []
    with db.engine.begin() as connection:
        sql_to_execute ="""
            SELECT name, power, health
            FROM hero
            JOIN recruitment ON hero.id = recruitment.hero_id
            JOIN guild ON recruitment.guild_id = guild.id
            WHERE guild.world_id = :world_id
            """
        
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"world_id": world_id})

        for row in result:
            heroes.append({
                "name": row.name,
                "power": row.power,
                "health": row.health
            })

    return {"heroes": heroes}
    # return {
    #     "success": True
    # }

# Get Quests - /world/get_quests/{world_id} (GET)
@router.get("/get_quests/{world_id}")
def get_quests():
    return [
            {
                "dungeon_name": "string",
                "level": "number",
            }
        ]

# Create Hero - /world/create_hero/{world_id} (POST)
@router.post("/create_hero/{world_id}")
def create_hero(hero: Hero):
    return {
        "success": True
    }

# Age Hero - /world/age_hero/{hero_id} (POST)
@router.post("/age_hero/{hero_id}")
def age_hero():
    return {
        "success": True
    }
