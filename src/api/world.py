from fastapi import APIRouter, Depends, HTTPException
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
    '''
    Attributes -
        hero_name: str
            name of the hero
        level: int
        age: int
            how old the hero is
        power: int
            how much damage the hero does
        health: int
        xp: int
    '''
    hero_name: str
    level: int
    age: int
    power: int
    health: int
    xp: int = 0


# Endpoints
# View Heroes - /world/view_heroes/{world_id} (GET)
@router.get("/view_heroes/{world_id}")
def view_heroes(world_id: int):
    '''
    Returns all heroes in the selected world
    Takes: world_id (int)
    Returns: list[Hero]
    '''

    heroes = []
    with db.engine.begin() as connection:
        sql_to_execute ="""
            SELECT name, level, power, age, health
            FROM hero
            WHERE guild_id IS NULL AND world_id = :world_id;
        """
        
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"world_id": world_id})

        for row in result:
            heroes.append({
                "name": row.name,
                "level": row.level,
                "power": row.power,
                "age": row.age,
                "health": row.health
            })

    return heroes

# Get Quests - /world/get_quests/{world_id} (GET)
@router.get("/get_quests/{world_id}")
def get_quests(world_id : int):
    '''
    Finds all dungeons that can be raided
    Takes: world_id (int)
    Returns: list[Dungeon]
    '''

    with db.engine.connect() as connection:
        # Fetch dungeon names and levels for the provided world_id
        result = connection.execute(
            sqlalchemy.text("""SELECT name, level FROM dungeon WHERE world_id = :world_id AND status = 'open'"""),
            {"world_id": world_id}
        )
        dungeons = [{"dungeon_name": row[0], "level": row[1]} for row in result.fetchall()]
    return dungeons

# Create Hero - /world/create_hero/{world_id} (POST)
@router.post("/create_hero/{world_id}")
def create_hero(world_id: int, hero: Hero):
    '''
    Creates a hero in a specified world
    Takes: world_id (int), Hero
    Returns: boolean on success or failure
    '''

    sql_to_execute = """
    INSERT INTO hero (name, level, age, power, health, xp, world_id)
    VALUES (:name, :level, :age, :power, :health, :xp, :world_id)
    """
    if hero.level < 0:
        raise HTTPException(status_code = 404, deatil = "Invalid Hero Level")
    if hero.age < 0:
        raise HTTPException(status_code = 404, detail = "Invalid Hero Age")
    if hero.power < 0:
        raise HTTPException(status_code = 404, detail = "Invalid Hero Power")
    if hero.health < 0:
        raise HTTPException(status_code = 404, detail = "Invalid Hero Health")
    if hero.xp < 0:
        raise HTTPException(status_code = 404, detail = "Invalid Hero xp")
    if world_id < 0:
        raise HTTPException(status_code = 404, detail = "Invalid World Id")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), {
            "name": hero.hero_name,
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
    '''
    Ages a hero
    Takes: hero_id (int)
    Returns: boolean on success or failure
    '''

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
