from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from typing import List

router = APIRouter(
    prefix="/dungeon",
    tags=["dungeon"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class Dungeon(BaseModel):
    dungeon_name: str
    dungeon_level: int
    player_capacity: int
    monster_capacity: int
    reward: int

class Monster(BaseModel):
    type: str
    health: int
    power: int
    level: int

class Hero(BaseModel):
    hero_name: str
    level: int
    power: int
    health: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

class GoldResponse(BaseModel):
    success: bool
    gold: int = None
    message: str = None

# Endpoints

@router.post("/create_dungeon/{world_id}", response_model=SuccessResponse)
def create_dungeon(world_id: int, dungeon: Dungeon):
    """
    Create a new dungeon in a specific world.

    Args:
        world_id (int): The ID of the world where the dungeon will be created.
        dungeon (Dungeon): The details of the dungeon to be created.

    Returns:
        SuccessResponse: Indicates whether the dungeon creation was successful.
    """

    if dungeon.dungeon_level < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Dungeon Level")
    if dungeon.player_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Player Capacity")
    if dungeon.monster_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Monster Capacity")
    if dungeon.reward < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Reward")
    if world_id < 0:
        raise HTTPException(status_code = 400, detail = "Invalid World Id")
        
    sql_to_execute = sqlalchemy.text("""
    INSERT INTO dungeon (name, level, party_capacity, monster_capacity, gold_reward, world_id)
    VALUES (:name, :level, :player_capacity, :monster_capacity, :reward, :world_id);
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "name": dungeon.dungeon_name,
            "level": dungeon.dungeon_level,
            "player_capacity": dungeon.player_capacity,
            "monster_capacity": dungeon.monster_capacity,
            "reward": dungeon.reward,
            "world_id": world_id
        })
        if result.rowcount > 0:
            return SuccessResponse(success=True, message="Dungeon created successfully")
        else:
            raise HTTPException(status_code = 400, detail = "Failed to create dungeon")

@router.post("/create_monster/{dungeon_id}", response_model=SuccessResponse)
def create_monster(dungeon_id: int, monsters: List[Monster]):
    """
    Create new monsters in a specific dungeon.

    Args:
        dungeon_id (int): The ID of the dungeon where the monsters will be created.
        monsters (List[Monster]): The list of monsters to be created.

    Returns:
        SuccessResponse: Indicates whether the monsters creation was successful.
    """

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

    # Validate input
    for monster in monsters:
        if monster.health < 0:
            raise HTTPException(status_code = 400, detail = "Invalid Monster Health")
        if dungeon_id < 0:
            raise HTTPException(status_code = 400, detail = "Invalid Dungeon Id")
        if monster.power < 0:
            raise HTTPException(status_code = 400, detail = "Invalid Monster Power")
        if monster.level < 0:
            raise HTTPException(status_code = 400, detail = "Invalid Monster Level")

    # Execute the query once with multiple rows
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), [
            {
                "type": monster.type,
                "health": monster.health,
                "dungeon_id": dungeon_id,
                "power": monster.power,
                "level": monster.level
            }
            for monster in monsters
        ])
        
        # Check if any rows were affected
        if result.rowcount > 0:
            return SuccessResponse(success=True, message="Monsters created successfully")
        else:
            raise HTTPException(status_code = 400, detail = "Failed to create monsters")

@router.post("/collect_bounty/{guild_id}", response_model=GoldResponse)
def collect_bounty(guild_id: int, dungeon_id: int):
    """
    Collect the bounty from a completed dungeon.

    Args: 
        guild_id (int): The ID of the guild collecting the bounty.
        dungeon_id (int): The ID of the dungeon to collect the bounty from.

    Returns:
        GoldResponse: Indicates whether the bounty collection was successful.

    Raises:
        HTTPException: If the dungeon status is not completed or attempting to collect bounty from a completed/open dungeon.
    """

    # Check if the dungeon status is completed
    with db.engine.begin() as connection:
        dungeon_status = connection.execute(
            sqlalchemy.text("SELECT status FROM dungeon WHERE id = :dungeon_id FOR UPDATE"),
            {"dungeon_id": dungeon_id}
        ).scalar()

    if dungeon_status == "completed" or dungeon_status == "open":
        raise HTTPException(status_code=400, detail="Cannot collect bounty from a completed or open dungeon")

    # Proceed with the bounty collection if the dungeon status is not completed
    sql_to_execute = sqlalchemy.text("""
    WITH monster_count AS (
        SELECT COUNT(*) AS count
        FROM monster
        WHERE dungeon_id = :dungeon_id AND health > 0
    ),
    guild_update AS (
        UPDATE guild
        SET gold = gold + (SELECT gold_reward FROM dungeon WHERE id = :dungeon_id)
        WHERE id = :guild_id
        AND (SELECT count FROM monster_count) = 0
        RETURNING gold
    ),
    dungeon_update AS (
        UPDATE dungeon
        SET status = 'completed'
        WHERE id = :dungeon_id
        AND NOT EXISTS (SELECT 1 FROM monster WHERE dungeon_id = :dungeon_id AND health > 0)
        RETURNING id
    ),
    hero_update AS (
        UPDATE hero
        SET dungeon_id = NULL
        WHERE dungeon_id = :dungeon_id AND health > 0
        RETURNING id
    )
    SELECT * FROM guild_update;
    """)

    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"dungeon_id": dungeon_id, "guild_id": guild_id})
        if result.rowcount > 0:
            gold = result.fetchone()[0]
            return GoldResponse(success=True, gold=gold, message="Bounty collected successfully")
        else:
            raise HTTPException(status_code=400, detail="Cannot collect bounty")


@router.get("/assess_damage/{dungeon_id}", response_model=list[Hero])
def assess_damage(guild_id: int, dungeon_id: int):
    """
    Assess the damage of heroes in a specific dungeon.

    Args:
        guild_id (int): The ID of the guild.
        dungeon_id (int): The ID of the dungeon.

    Returns:
        List[Hero]: List of heroes with health <= 0 in the specified dungeon.
    """

    sql_to_execute = """
    SELECT name, level, power, health
    FROM hero
    WHERE guild_id = :guild_id AND dungeon_id = :dungeon_id AND health <= 0
    """
    with db.engine.begin() as connection:
        heroes = connection.execute(sqlalchemy.text(sql_to_execute), {"guild_id": guild_id, "dungeon_id": dungeon_id})

    return [
        Hero(hero_name=hero.name, level=hero.level, power=hero.power, health=hero.health)
        for hero in heroes
    ]
