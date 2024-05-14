from fastapi import APIRouter, Depends
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
    with db.connection() as connection:
        result = connection.execute(
            f"""
            SELECT hero.id, hero.name, hero.level, hero.power
            FROM hero
            INNER JOIN guild ON hero.guild_id = guild.id
            INNER JOIN dungeon ON guild.world_id = dungeon.world_id
            WHERE dungeon.id = {dungeon_id}
            """
        )
        heroes = [
            {"id": row[0], "name": row[1], "level": row[2], "power": row[3]} 
            for row in result.fetchall()
        ]
    return heroes

# Attack Hero - /monster/attack_hero/{monster_id}/ (POST)
@router.post("/attack_hero/{monster_id}")
def attack_hero(hero_id: int, monster_id: int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text
        ("""
        UPDATE hero
        SET health = (SELECT health FROM hero WHERE id = :hero_id) - 
        (SELECT power FROM monster WHERE id = :monster_id)
        WHERE id = :hero_id
        """), [{"hero_id": hero_id, "monster_id": monster_id}])


    return {
        "success": "OK"
    }

# Die - /monster/die/{monster_id} (GET)
@router.get("/die/{monster_id}")
def die(monster_id: int):
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
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(sql_delete_monster), {"monster_id": monster_id})
        deleted_monster = result.fetchone()

    if deleted_monster:
        return {"success": True}
    else:
        return {"success": False, "message": "Monster is still alive or not found"}
