from fastapi import APIRouter, Depends, HTTPException
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
            return {"success": True}
        else:
            return {"success": False, "message": "Failed to create dungeon"}

@router.post("/create_monster/{dungeon_id}", response_model=SuccessResponse)
def create_monster(dungeon_id: int, monster: Monster):
    sql_to_execute = sqlalchemy.text("""
    INSERT INTO monster (type, health, dungeon_id, power, level)
    VALUES (:type, :health, :dungeon_id, :power, :level);
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "type": monster.type,
            "health": monster.health,
            "dungeon_id": dungeon_id,
            "power": monster.power,
            "level": monster.level
        })
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Failed to create monster"}

@router.post("/collect_bounty/{guild_id}", response_model=GoldResponse)
def collect_bounty(guild_id: int, dungeon_id: int):
    # Check if the dungeon status is completed
    with db.engine.begin() as connection:
        dungeon_status = connection.execute(
            sqlalchemy.text("SELECT status FROM dungeon WHERE id = :dungeon_id FOR UPDATE"),
            {"dungeon_id": dungeon_id}
        ).scalar()

    if dungeon_status == "completed":
        raise HTTPException(status_code=400, detail="Cannot collect bounty from a completed dungeon")

    # Proceed with the bounty collection if the dungeon status is not completed
    sql_to_execute = sqlalchemy.text("""
    WITH monster_count AS (
        SELECT COUNT(*) AS count
        FROM monster
        WHERE dungeon_id = :dungeon_id AND health > 0
        FOR UPDATE
    ),
    guild_update AS (
        UPDATE guild
        SET gold = gold + (SELECT gold_reward FROM dungeon WHERE id = :dungeon_id FOR UPDATE)
        WHERE id = :guild_id
        AND (SELECT count FROM monster_count) = 0
        RETURNING gold
    ),
    dungeon_update AS (
        UPDATE dungeon
        SET status = 'completed'
        WHERE id = :dungeon_id
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
            return {"success": True, "gold": gold}
        else:
            return {"success": False, "message": "Failed to collect bounty"}


@router.get("/assess_damage/{dungeon_id}", response_model=list[Hero])
def assess_damage(guild_id: int, dungeon_id: int):
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
