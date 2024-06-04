from fastapi import APIRouter, Depends
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
        player_capacity: int
            how many players max can be in the dungeon at a time
        monster_capacity: int
            how many monsters can be in the dungeon
        reward: int
            the gold awarded for clearing the dungeon
    '''
    dungeon_name: str
    dungeon_level: int
    player_capacity: int
    monster_capacity: int
    reward: int

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
    Creates a Dungeon at specified world_id
    Takes: world_id (int), Dungeon (dungeon_name, dungeon_level, player_capacity, monster_capacity, reward)
    Returns: boolean on success or failure of dungeon creation
    '''

    sql_to_execute = """
    INSERT INTO dungeon (name, level, player_capacity, monster_capacity, reward, world_id)
    VALUES (:name, :level, :player_capacity, :monster_capacity, :reward, :world_id);
    """
    with db.engine.begin() as connection:
        if dungeon.dungeon_level < 0:
            raise HTTPException("Invalid Dungeon Level")
        if dungeon.player_capacity < 0:
            raise HTTPException("Invalid Player Capacity")
        if dungeon.monster_capacity < 0:
            raise HTTPException("Invalid Monster Capacity")
        if dungeon.reward < 0:
            raise HTTPException("Invalid Reward")
        if world_id < 0:
            raise HTTPException("Invalid World Id")

        result = connection.execute(sql_to_execute, {
            "name": dungeon.dungeon_name,
            "level": dungeon.dungeon_level,
            "player_capacity": dungeon.player_capacity,
            "monster_capacity": dungeon.monster_capacity,
            "reward": dungeon.reward,
            "world_id": world_id
        })
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False}

# Create Monster - /dungeon/create_monster/{dungeon_id} (POST)
@router.post("/create_monster/{dungeon_id}")
def create_monster(dungeon_id: int, monsters: Monster):
    '''
    Creates a monster within the specified dungeon_id
    Takes: dungeon_id (int), Monster (type, health, power, level)
    Returns: boolean on success or failure of monster creation
    '''

    sql_to_execute = """
    INSERT INTO monster (type, health, dungeon_id, power, level)
    VALUES (:type, :health, :dungeon_id, :power, :level);
    """
    if monsters.health < 0:
        raise HTTPException("Invalid Monster Health")
    if dungeon_id < 0:
        raise HTTPException("Invalid Dungeon Id")
    if monsters.power < 0:
        raise HTTPException("Invalid Monster Power")
    if monsters.level < 0:
        raise HTTPException("Invalid Monster Level")

    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "type": monsters.type,
            "health": monsters.health,
            "dungeon_id": dungeon_id,
            "power": monsters.power,
            "level": monsters.level
        })

    return {
        "success": True
    }

# Collect Bounty - /dungeon/collect_bounty/{guild_id} (POST)
@router.post("/collect_bounty/{guild_id}")
def collect_bounty(guild_id: int, dungeon_id: int):
    '''
    Adds gold from cleared dungeon to guild
    Takes: guild_id (int), dungeon_id (int)
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
    Get query providing the heroes that survived from a dungeon quest
    Takes: guild_id (int), dungeon_id (int)
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