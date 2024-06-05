from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/monster",
    tags=["monster"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Find Heroes - /monster/find_heroes/{dungeon_id}/ (GET)
@router.get("/find_heroes/{dungeon_id}")
def find_heroes(dungeon_id: int):
    '''
    Get query returning all heroes in a dungeon\n
    Takes: dungeon_id (int)\n
    Returns: list[Hero]
    '''

    with db.engine.begin() as connection:
        try:
            result = connection.execute(
                sqlalchemy.text("""
                SELECT hero.id, hero.name, hero.level, hero.power
                FROM hero
                JOIN guild ON hero.guild_id = guild.id
                JOIN dungeon ON guild.world_id = dungeon.world_id AND dungeon.id = hero.dungeon_id
                WHERE dungeon.id = :dungeon_id and hero.health > 0
                """
            ), {"dungeon_id": dungeon_id})
            heroes = [
                {"id": row.id, "name": row.name, "level": row.level, "power": row.power} 
                for row in result.fetchall()
            ]
        except sqlalchemy.exc.IntegrityError as http:
            raise HTTPException(status_code=404, detail="Unable to find heros in the dungeon")
    return heroes

# Attack Hero - /monster/attack_hero/{monster_id}/ (POST)
@router.post("/attack_hero/{monster_id}")
def attack_hero(hero_id: int, monster_id: int):
    '''
    Monster deals damage to a hero\n
    Takes: hero_id (int), monster_id (int)\n
    Returns: boolean on success or failure
    '''

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text
        ("""
        UPDATE hero
        SET health = (SELECT health FROM hero WHERE id = :hero_id) - 
        (SELECT power FROM monster WHERE id = :monster_id)
        WHERE id = :hero_id
        """), [{"hero_id": hero_id, "monster_id": monster_id}])

        connection.execute(sqlalchemy.text(
        """
        INSERT INTO targeting (hero_id, monster_id)
        VALUES (:hero_id, :monster_id)
        """), [{"hero_id": hero_id, "monster_id": monster_id}]
        )

        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero not found"}


# Die - /monster/die/{monster_id} (GET)
@router.post("/die/{monster_id}")
def die(monster_id: int):
    '''
    Sets the status of monster to dead and removes prior targeting of heroes\n
    Takes: monster_id (int)\n
    Returns: boolean on success or failure
    '''

    sql_delete_monster = """
    WITH deleted_targeting AS (
        DELETE FROM targeting
        WHERE monster_id = :monster_id
        RETURNING *
    ),
    deleted_monster AS (
        DELETE FROM monster
        WHERE id = :monster_id AND health <= 0
        RETURNING *
    )
    SELECT * FROM deleted_monster;
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_delete_monster), {"monster_id": monster_id})
        deleted_monster = result.fetchone()

    if deleted_monster:
        return {"success": True}
    else:
        return {"success": False, "message": "Monster is still alive or not found"}
