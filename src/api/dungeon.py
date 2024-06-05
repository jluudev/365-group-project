from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/dungeon",
    tags=["dungeon"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class Dungeon(BaseModel):
    '''
    Attributes -
        dungeon_name: str
            name of the dungeon
        dungeon_level: int
            level of the dungeon
        party_capacity: int
            how many players max can be in the dungeon at a time
        monster_capacity: int
            how many monsters can be in the dungeon
        gold_reward: int
            the gold awarded for clearing the dungeon
    '''
    dungeon_name: str
    dungeon_level: int
    party_capacity: int
    monster_capacity: int
    gold_reward: int

class Monster(BaseModel):
    '''
    Attributes -
        type: str
            category of monster (ex. Coconut Slime, BigFoot, Giant Ant)
        health: int
            hit points of the monster
        power: int
            how much damage the monster does
        level: int
            the level of the monster
    '''
    type: str
    health: int
    power: int
    level: int

class Hero(BaseModel):
    '''
    Attributes -
        hero_name: str
            the name of the hero
    '''
    hero_name: str
    
# Endpoint

# Create Dungeon - /dungeon/create_dungeon/{world_id} (POST)
@router.post("/create_dungeon/{world_id}")
def create_dungeon(world_id: int, dungeon: Dungeon):
    '''
    Creates a Dungeon at specified world_id\n
    Takes: world_id (int), Dungeon (dungeon_name, dungeon_level, party_capacity, monster_capacity, gold_reward)\n
    Returns: boolean on success or failure of dungeon creation
    '''

    sql_to_execute = """
    WITH dungeon_count AS (
        SELECT COUNT(*) AS current_dungeon_count
        FROM dungeon
        WHERE world_id = :world_id
    ),
    capacity_check AS (
        SELECT dungeon_capacity
        FROM world
        WHERE id = :world_id
    )
    INSERT INTO dungeon (name, level, party_capacity, monster_capacity, gold_reward, world_id)
    SELECT :name, :level, :party_capacity, :monster_capacity, :gold_reward, :world_id
    FROM dungeon_count, capacity_check
    WHERE dungeon_count.current_dungeon_count < capacity_check.dungeon_capacity
    RETURNING id
    """
    if dungeon.dungeon_level < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Dungeon Level")
    if dungeon.party_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Player Capacity")
    if dungeon.monster_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Monster Capacity")
    if dungeon.gold_reward < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Gold Reward")
    if world_id < 0:
        raise HTTPException(status_code = 400, detail = "Invalid World Id")
    
    with db.engine.begin() as connection:
        try:
            result = connection.execute(sqlalchemy.text(sql_to_execute), {
                "name": dungeon.dungeon_name,
                "level": dungeon.dungeon_level,
                "party_capacity": dungeon.party_capacity,
                "monster_capacity": dungeon.monster_capacity,
                "gold_reward": dungeon.gold_reward,
                "world_id": world_id
            })
            if result.rowcount > 0:
                return {"success": True, "message": "dungeon %d created" % result.fetchone().id}
            else:
                return {"success": False, "message": "World %d at max dungeon capacity" % world_id}
        except sqlalchemy.exc.IntegrityError as http:
            return {"success": False, "message": "Dungeon name must be unique within specified world %d" % world_id}

# Create Monster - /dungeon/create_monster/{dungeon_id} (POST)
@router.post("/create_monster/{dungeon_id}")
def create_monster(dungeon_id: int, monsters: Monster):
    '''
    Creates a monster within the specified dungeon_id\n
    Takes: dungeon_id (int), Monster (type, health, power, level)\n
    Returns: boolean on success or failure of monster creation
    '''

    sql_to_execute = """
    WITH monster_count AS (
        SELECT COUNT(*) AS current_monster_count
        FROM monster
        WHERE dungeon_id = :dungeon_id
    ),
    capacity_check AS (
        SELECT monster_capacity
        FROM dungeon
        WHERE id = :dungeon_id
    )
    INSERT INTO monster (type, health, dungeon_id, power, level)
    SELECT :type, :health, :dungeon_id, :power, :level
    FROM monster_count, capacity_check
    WHERE monster_count.current_monster_count < capacity_check.monster_capacity;
    """
    if monsters.health < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Monster Health")
    if dungeon_id < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Dungeon Id")
    if monsters.power < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Monster Power")
    if monsters.level < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Monster Level")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), {
            "type": monsters.type,
            "health": monsters.health,
            "dungeon_id": dungeon_id,
            "power": monsters.power,
            "level": monsters.level
        })
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Dungeon at max monster capacity"}

# Collect Bounty - /dungeon/collect_bounty/{guild_id} (POST)
@router.post("/collect_bounty/{guild_id}")
def collect_bounty(guild_id: int, dungeon_id: int):
    '''
    Adds gold from cleared dungeon to guild\n
    Takes: guild_id (int), dungeon_id (int)\n
    Returns: gold (int) on success, boolean False on failure
    '''

    # Only collect bounty if no monsters are alive (no monsters with that dungeon_id)
    sql_to_execute = sqlalchemy.text("""
    WITH monster_count AS (
    SELECT COUNT(*) AS count
    FROM monster
    WHERE dungeon_id = :dungeon_id AND health > 0
    )
    UPDATE guild
    SET gold = gold + (SELECT gold_reward FROM dungeon WHERE id = :dungeon_id)
    WHERE id = :guild_id
    AND (SELECT count FROM monster_count) = 0
    RETURNING gold;
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"dungeon_id": dungeon_id, "guild_id": guild_id})
        if result.rowcount > 0:
            # Return the amount of gold collected
            return {"gold": result.fetchone()[0]}
        else:
            return {"success": False, "message": "Failed to collect bounty"}

# Assess Damage - /dungeon/assess_damage/{dungeon_id} (GET)
@router.get("/assess_damage/{dungeon_id}")
def assess_damage(guild_id: int, dungeon_id: int):
    '''
    Get query providing the heroes that survived from a dungeon quest\n
    Takes: guild_id (int), dungeon_id (int)\n
    Returns: list[Hero]
    '''

    sql_to_execute = """
    SELECT name, level, power, health
    FROM hero
    WHERE guild_id = :guild_id AND dungeon_id = :dungeon_id AND health <= 0
    """
    with db.engine.begin() as connection:
        heroes = connection.execute(sqlalchemy.text(sql_to_execute), {"guild_id": guild_id, "dungeon_id": dungeon_id})

    returning_heroes = []
    for hero in heroes:
        returning_heroes.append(
            {
                "hero_name": hero.name,
                "level": hero.level,
                "power": hero.power,
                "health": hero.health
            }
        )
    return returning_heroes