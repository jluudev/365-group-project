from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/monster",
    tags=["monster"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class HeroDetails(BaseModel):
    id: int
    name: str
    level: int
    power: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

# Endpoints

@router.get("/find_heroes/{dungeon_id}", response_model=list[HeroDetails])
def find_heroes(dungeon_id: int):
    """
    Find heroes in a specific dungeon.

    Args:
        dungeon_id (int): The ID of the dungeon.

    Returns:
        List[HeroDetails]: List of heroes found in the specified dungeon.
    """

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT hero.id, hero.name, hero.level, hero.power
            FROM hero
            JOIN guild ON hero.guild_id = guild.id
            JOIN dungeon ON guild.world_id = dungeon.world_id AND dungeon.id = hero.dungeon_id
            WHERE dungeon.id = :dungeon_id AND hero.health > 0
            """), {"dungeon_id": dungeon_id}
        )
        heroes = [
            HeroDetails(id=row[0], name=row[1], level=row[2], power=row[3]) 
            for row in result.fetchall()
        ]
    return heroes

@router.post("/attack_hero/{monster_id}", response_model=SuccessResponse)
def attack_hero(hero_id: int, monster_id: int):
    """
    Attack a hero with a monster.

    Args:
        hero_id (int): The ID of the hero to be attacked.
        monster_id (int): The ID of the monster attacking the hero.

    Returns:
        SuccessResponse: Indicates whether the attack was successful.
    """
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            UPDATE hero
            SET health = (SELECT health FROM hero WHERE id = :hero_id) - 
            (SELECT power FROM monster WHERE id = :monster_id)
            WHERE id = :hero_id
        """), {"hero_id": hero_id, "monster_id": monster_id})

        connection.execute(sqlalchemy.text("""
            INSERT INTO targeting (hero_id, monster_id)
            VALUES (:hero_id, :monster_id)
        """), {"hero_id": hero_id, "monster_id": monster_id})

        if result.rowcount > 0:
            return SuccessResponse(success=True, message="Hero attacked successfully")
        else:
            raise HTTPException(status_code = 400, detail = "Failed to attack hero")

