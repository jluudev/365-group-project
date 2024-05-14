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
    power: int
    health: int
    xp: int = 0


# Endpoints
# View Heroes - /world/view_heroes/{world_id} (GET)
@router.get("/view_heroes/{world_id}")
def view_heroes(world_id: int):

    heroes = []
    with db.engine.begin() as connection:
        sql_to_execute ="""
            SELECT name, power, health
            FROM hero
            WHERE guild_id IS NULL AND world_id = :world_id;
        """
        
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"world_id": world_id})

        for row in result:
            heroes.append({
                "name": row.name,
                "power": row.power,
                "health": row.health
            })

    return heroes
    # return {
    #     "success": True
    # }

# Get Quests - /world/get_quests/{world_id} (GET)
@router.get("/get_quests/{world_id}")
def get_quests(world_id : int):
    with db.connection() as connection:
        # Fetch dungeon names and levels for the provided world_id
        result = connection.execute(
            sqlalchemy.text("SELECT name, level FROM dungeon WHERE world_id = :world_id"),
            {"world_id": world_id}
        )
        dungeons = [{"dungeon_name": row[0], "level": row[1]} for row in result.fetchall()]
    return dungeons

# Create Hero - /world/create_hero/{world_id} (POST)
@router.post("/create_hero/{world_id}")
def create_hero(world_id: int, hero: Hero):
    sql_to_execute = """
    INSERT INTO hero (name, class, level, age, power, health, xp, world_id)
    VALUES (:name, :classType, :level, :age, :power, :health, :xp, :world_id);
    """
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "name": hero.hero_name,
            "classType": hero.classType,
            "level": hero.level,
            "age": hero.age,
            "power": hero.power,
            "health": hero.health,
            "xp": hero.xp,
            "world_id": world_id
        })
        
        # Success if the hero is created
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero not created"}


# Age Hero - /world/age_hero/{hero_id} (POST)
@router.post("/age_hero/{hero_id}")
def age_hero(hero_id: int):
    sql_to_execute = """
    UPDATE hero
    SET age = age + 1
    WHERE id = :hero_id;
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"hero_id": hero_id})
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero not found"}
