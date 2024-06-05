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
    id: int
    name: str
    power: int
    health: int

class DungeonQuest(BaseModel):
    dungeon_id: int
    dungeon_name: str
    level: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

# Endpoints

@router.get("/view_heroes/{world_id}", response_model=list[HeroView])
def view_heroes(world_id: int):
    """
    View heroes not in a guild in a specific world.

    Args:
        world_id (int): The ID of the world.

    Returns:
        List[HeroView]: List of heroes in the specified world.
    """
    heroes = []
    with db.engine.begin() as connection:
        sql_to_execute = """
            SELECT id, name, power, health
            FROM hero
            WHERE guild_id IS NULL AND world_id = :world_id;
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"world_id": world_id})

        heroes = [
            HeroView(id=row.id, name=row.name, power=row.power, health=row.health) 
            for row in result
        ]

    return heroes

@router.get("/get_quests/{world_id}", response_model=list[DungeonQuest])
def get_quests(world_id: int):
    """
    Get quests (open dungeons) available in a specific world.

    Args:
        world_id (int): The ID of the world.

    Returns:
        List[DungeonQuest]: List of quests available in the specified world.
    """
    with db.engine.connect() as connection:
        result = connection.execute(
            sqlalchemy.text("""SELECT id, name, level FROM dungeon WHERE world_id = :world_id AND status = 'open'"""),
            {"world_id": world_id}
        )
        dungeons = [
            DungeonQuest(dungeon_id=row[0], dungeon_name=row[1], level=row[2]) 
            for row in result.fetchall()
        ]
    return dungeons

@router.post("/create_hero/{world_id}", response_model=SuccessResponse)
def create_hero(world_id: int, hero: Hero):
    """
    Create a new hero in a specific world.

    Args:
        world_id (int): The ID of the world where the hero will be created.
        hero (Hero): The details of the hero to be created.

    Returns:
        SuccessResponse: Indicates whether the hero creation was successful.
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
        
@router.get("/get_worlds", response_model=list[dict])
def get_worlds():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT id, name FROM world"))
        worlds = [{"id": row.id, "name": row.name} for row in result.fetchall()]
    return worlds
