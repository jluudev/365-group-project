from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/world",
    tags=["world"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class Hero(BaseModel):
    hero_name: str
    classType: str
    level: int
    age: int
    power: int
    health: int
    xp: int = 0

class HeroView(BaseModel):
    name: str
    power: int
    health: int

class DungeonQuest(BaseModel):
    dungeon_name: str
    level: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

# Endpoints

@router.get("/view_heroes/{world_id}", response_model=list[HeroView])
def view_heroes(world_id: int):
    heroes = []
    with db.engine.begin() as connection:
        sql_to_execute = """
            SELECT name, power, health
            FROM hero
            WHERE guild_id IS NULL AND world_id = :world_id;
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"world_id": world_id})

        heroes = [
            HeroView(name=row.name, power=row.power, health=row.health) 
            for row in result
        ]

    return heroes

@router.get("/get_quests/{world_id}", response_model=list[DungeonQuest])
def get_quests(world_id: int):
    with db.engine.connect() as connection:
        result = connection.execute(
            sqlalchemy.text("""SELECT name, level FROM dungeon WHERE world_id = :world_id AND status = 'open'"""),
            {"world_id": world_id}
        )
        dungeons = [
            DungeonQuest(dungeon_name=row[0], level=row[1]) 
            for row in result.fetchall()
        ]
    return dungeons

@router.post("/create_hero/{world_id}", response_model=SuccessResponse)
def create_hero(world_id: int, hero: Hero):
    sql_to_execute = sqlalchemy.text("""
    INSERT INTO hero (name, class, level, age, power, health, xp, world_id)
    VALUES (:name, :classType, :level, :age, :power, :health, :xp, :world_id);
    """)
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

        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero not created"}

@router.post("/age_hero/{hero_id}", response_model=SuccessResponse)
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
