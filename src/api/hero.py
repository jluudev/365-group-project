from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import func
from src import database as db

router = APIRouter(
    prefix="/hero",
    tags=["hero"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class HeroXP(BaseModel):
    xp: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

class PendingRequest(BaseModel):
    guild_name: str
    gold: int

class Monster(BaseModel):
    id: int
    name: str
    level: int
    health: int
    power: int

class HealthResponse(BaseModel):
    health: int

class HeroMonsterInteraction(BaseModel):
    monster_id: int
    monster_type: str
    monster_level: int
    initial_health: int
    remaining_health: int
    damage_dealt: int
    monster_power: int
    battle_time: str
    monster_defeated: bool

class HeroMonsterInteractionsResponse(BaseModel):
    status: str
    hero_id: int
    total_battles: int
    monsters_defeated: int
    total_damage_dealt: int
    battle_details: list[HeroMonsterInteraction]

class Hero(BaseModel):
    id: int
    level: int
    xp: int

class UpdatedHero(BaseModel):
    xp: int
    updated_xp: int
    updated_level: int

# Endpoints

@router.get("/check_xp/{hero_id}", response_model=HeroXP)
def check_xp(hero_id: int):
    """
    Check the experience points (XP) of a hero.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        HeroXP: The experience points of the hero.
    """

    with db.engine.begin() as connection:
        xp = connection.execute(sqlalchemy.text("""
            SELECT xp
            FROM hero
            WHERE id = :hero_id
        """), {"hero_id": hero_id}).scalar_one()
    return {"xp": xp}

@router.post("/raise_level/{hero_id}", response_model=SuccessResponse)
def raise_level(hero_id: int):
    """
    Raise the level of a hero if they have enough experience points.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        SuccessResponse: Indicates whether the level raise was successful.
    """

    sql_to_execute = """
    WITH hero AS (
        SELECT id, level, xp
        FROM hero
        WHERE id = :hero_id
    ),
    updated_hero AS (
        UPDATE hero
        SET level = level + 1, xp = xp - 100
        WHERE id = :hero_id AND xp >= 100
        RETURNING id, level, xp
    )
    SELECT
        hero.xp,
        updated_hero.xp as updated_xp,
        updated_hero.level as updated_level
    FROM hero
    LEFT JOIN updated_hero ON updated_hero.id = hero.id
    """
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"hero_id": hero_id})

        if result.rowcount == 0:
            return {"success": False, "message": f"No hero matching id {hero_id}"}

        row = result.fetchone()
        if row:
            updated_hero = UpdatedHero(
                xp=row[0],
                updated_xp=row[1],
                updated_level=row[2]
            )

            if updated_hero.updated_level is not None:
                return {"success": True, "message": f"Hero id #{hero_id}: level={updated_hero.updated_level}, xp={updated_hero.updated_xp}"}
            else:
                return {"success": False, "message": f"Not enough XP to raise level, current xp of hero {hero_id}: {updated_hero.xp}"}
        else:
            return {"success": False, "message": f"No rows returned for hero id {hero_id}"}


@router.get("/view_pending_requests/{hero_id}", response_model=list[PendingRequest])
def view_pending_requests(hero_id: int):
    """
    View pending requests for a hero.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        List[PendingRequest]: List of pending requests for the hero.
    """
    requests = []
    with db.engine.begin() as connection:
        recruit = connection.execute(sqlalchemy.text("""
            SELECT name, gold 
            FROM recruitment 
            JOIN guild ON recruitment.guild_id = guild.id 
            WHERE recruitment.hero_id = :id
        """), {"id": hero_id})
        for request in recruit:
            requests.append({"guild_name": request.name, "gold": request.gold})
    return requests

@router.post("/accept_request/{hero_id}", response_model=SuccessResponse)
def accept_request(hero_id: int, guild_name: str):
    """
    Accept a pending request for a hero to join a guild.

    Args:
        hero_id (int): The ID of the hero.
        guild_name (str): The name of the guild.

    Returns:
        SuccessResponse: Indicates whether the request was accepted.
    """
    sql_to_execute = sqlalchemy.text("""
    WITH guild_info AS (
        SELECT g.id AS guild_id, g.player_capacity
        FROM guild g
        WHERE g.name = :guild_name
        FOR UPDATE
    ),
    current_hero_count AS (
        SELECT COUNT(*) AS current_heroes
        FROM hero h
        WHERE h.guild_id IN (SELECT guild_id FROM guild_info)
    ),
    update_hero AS (
        UPDATE hero
        SET guild_id = (SELECT guild_id FROM guild_info)
        WHERE id = :hero_id AND guild_id IS NULL AND
              (SELECT current_heroes FROM current_hero_count) < (SELECT player_capacity FROM guild_info)
        RETURNING guild_id
    )
    UPDATE recruitment
    SET status = 'accepted', response_date = now()
    WHERE hero_id = :hero_id AND guild_id IN (SELECT guild_id FROM update_hero)
    RETURNING hero_id;
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"guild_name": guild_name, "hero_id": hero_id})
        hero_updated = result.fetchone()
        if hero_updated:
            return {"success": True}
        else:
            raise HTTPException(status_code=400, detail="Request not found or hero already in a guild or guild is full")

@router.post("/attack_monster/{hero_id}", response_model=SuccessResponse)
def attack_monster(hero_id: int, monster_id: int):
    """
    Attack a monster with a hero.

    Args:
        hero_id (int): The ID of the hero.
        monster_id (int): The ID of the monster.

    Returns:
        SuccessResponse: Indicates whether the attack was successful.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT m.health AS monster_health, h.power AS hero_power
            FROM monster m
            JOIN hero h ON h.id = :hero_id
            WHERE m.id = :monster_id
            FOR UPDATE
        """), {"monster_id": monster_id, "hero_id": hero_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Hero or Monster not found")
        
        monster_health = result.monster_health
        hero_power = result.hero_power
        new_health = monster_health - hero_power
        damage = hero_power

        connection.execute(sqlalchemy.text("""
            UPDATE monster
            SET health = :new_health
            WHERE id = :monster_id
        """), {"new_health": new_health, "monster_id": monster_id})

        connection.execute(sqlalchemy.text("""
            INSERT INTO targeting (hero_id, monster_id, damage, timestamp)
            VALUES (:hero_id, :monster_id, :damage, CURRENT_TIMESTAMP)
        """), {"hero_id": hero_id, "monster_id": monster_id, "damage": damage})

    return SuccessResponse(success=True, message="Monster attacked successfully")

@router.get("/check_health/{hero_id}", response_model=HealthResponse)
def check_health(hero_id: int):
    """
    Check the health of a hero.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        HealthResponse: The current health of the hero.
    """

    with db.engine.begin() as connection:
        health = connection.execute(sqlalchemy.text("""
            SELECT health
            FROM hero
            WHERE id = :hero_id
        """), {"hero_id": hero_id}).scalar_one()
    return HealthResponse(health=health)

@router.post("/run_away/{hero_id}", response_model=SuccessResponse)
def run_away(hero_id: int):
    """
    Run away from a dungeon. Hero can only run away if they are not being targeted by a monster.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        SuccessResponse: Indicates whether the hero successfully ran away.
    """
    
    sql_to_execute = """
    SELECT COUNT(*) 
    FROM targeting 
    WHERE hero_id = :hero_id;
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"hero_id": hero_id})
        row_count = result.fetchone()[0]
        if row_count > 0:
            return {"success": False, "message": "Cannot run away while being targeted by a monster"}
        else:
            update_sql = """
                UPDATE hero
                SET dungeon_id = NULL
                WHERE id = :hero_id;
            """
            update = connection.execute(sqlalchemy.text(update_sql), {"hero_id": hero_id})
            if update.rowcount > 0:
                return SuccessResponse(success=True, message="Hero successfully ran away")
            else:
                raise HTTPException(status_code=404, detail="Hero cannot run away")

@router.get("/find_monsters/{dungeon_id}", response_model=list[Monster])
def find_monsters(dungeon_id: int):
    """
    Find monsters in a specific dungeon.

    Args:
        dungeon_id (int): The ID of the dungeon.

    Returns:
        List[Monster]: List of monsters found in the specified dungeon.
    """

    sql_to_execute = """
    SELECT id, type AS name, level, health, power
    FROM monster
    WHERE dungeon_id = :dungeon_id AND monster.health > 0
    """
    with db.engine.begin() as connection:
        monsters = connection.execute(sqlalchemy.text(sql_to_execute), {"dungeon_id": dungeon_id})

    return [Monster(id=monster.id, name=monster.name, level=monster.level, health=monster.health, power=monster.power) for monster in monsters]

@router.get("/{hero_id}/monster_interactions", response_model=HeroMonsterInteractionsResponse)
def hero_monster_interactions(hero_id: int):
    """
    Get the battle history of a hero.

    Args:
        hero_id (int): The ID of the hero.

    Returns:
        HeroMonsterInteractionsResponse: The battle history details of the hero.
    """

    sql_monster_interactions = """
    WITH hero_battles AS (
        SELECT
            t.hero_id,
            t.monster_id,
            m.type AS monster_type,
            m.level AS monster_level,
            m.health AS monster_remaining_health,
            m.power AS monster_power,
            t.timestamp AS battle_time,
            SUM(t.damage) OVER (PARTITION BY t.monster_id ORDER BY t.timestamp RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) + FIRST_VALUE(m.health) OVER (PARTITION BY t.monster_id ORDER BY t.timestamp ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS initial_health,
            SUM(t.damage) OVER (PARTITION BY t.monster_id ORDER BY t.timestamp ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS damage_dealt,
            CASE WHEN m.health <= 0 THEN 1 ELSE 0 END AS monster_defeated
        FROM targeting t
        JOIN monster m ON t.monster_id = m.id
        WHERE t.hero_id = :hero_id
    ),
    battle_summary AS (
        SELECT
            hero_id,
            COUNT(DISTINCT monster_id) AS total_battles,
            SUM(monster_defeated::int) AS monsters_defeated,
            SUM(damage_dealt) AS total_damage_dealt
        FROM hero_battles
        GROUP BY hero_id
    )
    SELECT
        hb.hero_id,
        hb.monster_id,
        hb.monster_type,
        hb.monster_level,
        hb.initial_health,
        hb.monster_remaining_health AS remaining_health,
        hb.damage_dealt,
        hb.monster_power,
        to_char(hb.battle_time, 'YYYY-MM-DD HH24:MI:SS') AS battle_time,  -- Convert timestamp to string format
        bs.total_battles,
        bs.monsters_defeated,
        bs.total_damage_dealt
    FROM hero_battles hb
    JOIN battle_summary bs ON hb.hero_id = bs.hero_id
    ORDER BY hb.battle_time DESC;
    """
    with db.engine.begin() as connection:
        interactions = connection.execute(sqlalchemy.text(sql_monster_interactions), {"hero_id": hero_id}).fetchall()

    if not interactions:
        raise HTTPException(status_code=404, detail="No interactions found for the specified hero")

    return HeroMonsterInteractionsResponse(
        status="success",
        hero_id=interactions[0].hero_id,
        total_battles=interactions[0].total_battles,
        monsters_defeated=interactions[0].monsters_defeated,
        total_damage_dealt=interactions[0].total_damage_dealt,
        battle_details=[
            HeroMonsterInteraction(
                monster_id=row.monster_id,
                monster_type=row.monster_type,
                monster_level=row.monster_level,
                initial_health=row.initial_health,
                remaining_health=row.remaining_health,
                damage_dealt=row.damage_dealt,
                monster_power=row.monster_power,
                battle_time=row.battle_time,
                monster_defeated=bool(row.remaining_health <= 0)
            )
            for row in interactions
        ]
    )
