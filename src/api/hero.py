from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/hero",
    tags=["hero"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model

# Endpoints

# Check XP - /hero/check_xp/{hero_id} (POST)
@router.get("/check_xp/{hero_id}")
def check_xp(hero_id: int):
    '''
    TODO this does not have an error if there is no hero_id that is matched
    Returns the xp of a selected hero_id
    Takes: hero_id (int)
    Returns: int
    '''

    with db.engine.begin() as connection:
        xp = connection.execute(sqlalchemy.text
            ("""
            SELECT xp
            FROM hero
            WHERE id = :hero_id
            """), [{"hero_id": hero_id}]
        ).scalar_one()
    return {
        "xp": xp
    }

# Raise Level - /hero/raise_level/{hero_id} (POST)
@router.post("/raise_level/{hero_id}")
def raise_level(hero_id: int):
    '''
    increases the level of the hero by 1 if they meet xp threshold
    Takes: hero_id (int)
    Returns: boolean on success or failure
    '''

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text
        ("""
        UPDATE hero
        SET level = level + 1, xp = xp - 100
        WHERE id = :hero_id AND xp >= 100
        """), [{"hero_id": hero_id}])
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Not enough XP to raise level"}

# View Pending Requests - /hero/view_pending_requests/{hero_id} (GET)
@router.get("/view_pending_requests/{hero_id}")
def view_pending_requests(hero_id: int):
    '''
    Get query to see all pending requests for hero_id from guilds
    Takes: hero_id (int)
    Returns: list[Request] (guild_name (TEXT), gold (int))
    '''

    requests = []
    with db.engine.begin() as connection:
        recruit = connection.execute(sqlalchemy.text
        ("""SELECT name, gold 
        FROM recruitment 
        JOIN guild ON recruitment.guild_id = guild.id 
        WHERE recruitment.hero_id = :id"""), [{"id": hero_id}])

        for request in recruit:
            requests.append({
                "guild_name": request.name,
                "gold": request.gold
            })

    return requests

# Accept Request - /hero/accept_request/{hero_id} (POST)
@router.post("/accept_request/{hero_id}")
def accept_request(hero_id: int, guild_name: str):
    '''
    Recruits hero to guild
    Takes: hero_id (int), guild_name (str)
    Returns: boolean on success
    Throws HTTPException if request not found, hero already in guild, or guild is full
    '''

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

# Attack Monster - /hero/attack_monster/{hero_id}/ (POST)
@router.post("/attack_monster/{hero_id}")
def attack_monster(monster_id: int, hero_id: int):
    '''
    Hero attacks monster, dealing damage
    Takes: monster_id (int), hero_id (int)
    Returns: boolean on success
    Throws HTTPException if hero_id or monster_id not found in db
    '''

    with db.engine.begin() as connection:
        # Lock the rows for update to handle concurrency
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

        # Calculate the new health of the monster
        new_health = monster_health - hero_power
        damage = hero_power

        # Update the health of the monster
        connection.execute(sqlalchemy.text("""
            UPDATE monster
            SET health = :new_health
            WHERE id = :monster_id
        """), {"new_health": new_health, "monster_id": monster_id})

        # Log the attack in the targeting table
        connection.execute(sqlalchemy.text("""
            INSERT INTO targeting (hero_id, monster_id, damage, timestamp)
            VALUES (:hero_id, :monster_id, :damage, CURRENT_TIMESTAMP)
        """), {"hero_id": hero_id, "monster_id": monster_id, "damage": damage})

    return {
        "success": "OK"
    }

# Check Health - /hero/check_health/{hero_id}/ (GET)
@router.get("/check_health/{hero_id}")
def check_health(hero_id: int):
    '''
    TODO no error checking if hero_id not found
    Get query to recieve the health of a hero by hero_id
    Takes: hero_id (int)
    Returns: int
    '''
    with db.engine.begin() as connection:
        health = connection.execute(sqlalchemy.text
        ("""
        SELECT health
        FROM hero
        WHERE id = :hero_id
        """), [{"hero_id": hero_id}]).scalar_one()
    return {
        "health": health
    }

# Run Away - /hero/run_away/{hero_id}/ (POST)
@router.post("/run_away/{hero_id}")
def run_away(hero_id: int):
    '''
    TODO I think it should throw an error if unable to update location, boolean if can't escape
    Has an individual hero escape from a dungeon inbetween combat encounters
    Takes: hero_id (int)
    Returns: boolean on success or failure
    '''

    # Check if the hero is targeted by any monster
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
                return {"success": True}
            else:
                return {"success": False, "message": "Failed to update hero's location"}
    

# Die - /hero/die/{hero_id}/ (POST)
@router.post("/die/{hero_id}")
def die(hero_id: int):
    '''
    Sets the status of hero to dead and removes prior targeting of monsters
    Takes: hero_id (int)
    Returns: boolean on success or failure
    '''

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text
        ("""
        UPDATE hero
        SET status = 'dead'
        WHERE id = :hero_id AND health <= 0
        """), [{"hero_id": hero_id}])

        # remove any targeting
        connection.execute(sqlalchemy.text
        ("""
        DELETE FROM targeting
        WHERE hero_id = :hero_id
        """), [{"hero_id": hero_id}])

        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Hero is still alive or not found"}

# Find Monsters - /hero/find_monsters/{dungeon_id}/ (GET)
@router.get("/find_monsters/{dungeon_id}")
def find_monsters(dungeon_id: int):
    '''
    Get query that returns all monsters in a dungeon by dungeon_id
    Takes: dungeon_id (int)
    Returns: list[Monster]
    '''

    sql_to_execute = """
    SELECT id, type AS name, level, health, power
    FROM monster
    WHERE dungeon_id = :dungeon_id AND monster.health > 0
    """
    with db.engine.begin() as connection:
        monsters = connection.execute(sqlalchemy.text(sql_to_execute), {"dungeon_id": dungeon_id})

    monster_list = []
    for monster in monsters:
        monster_list.append(
            {
                "id": monster.id,
                "name" : monster.name,
                "level": monster.level,
                "health": monster.health,
                "power": monster.power
            }
        )
    return monster_list

@router.get("/{hero_id}/monster_interactions")
def hero_monster_interactions(hero_id: int):
    '''
    Provides detailed insights into a hero's interactions with monsters
    Takes: hero_id (int)
    Returns: json response
        - "status" boolean on success or failure
        - "hero_id" (int)
        - "total_battles" (int)
        - "monsters_defeated" (int)
        - "total_damage_dealt" (int)
        - "battle_details" (monster_id (int),
                            monster_type (TEXT),
                            monster_level (int),
                            initial_health (int),
                            remaining_health (int),
                            damage_dealt (int),
                            monster_power (int),
                            battle_time (int),
                            monster_defeated (bool))
    '''

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
        hb.battle_time,
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

    response = {
        "status": "success",
        "hero_id": interactions[0].hero_id,
        "total_battles": interactions[0].total_battles,
        "monsters_defeated": interactions[0].monsters_defeated,
        "total_damage_dealt": interactions[0].total_damage_dealt,
        "battle_details": [
            {
                "monster_id": row.monster_id,
                "monster_type": row.monster_type,
                "monster_level": row.monster_level,
                "initial_health": row.initial_health,
                "remaining_health": row.remaining_health,
                "damage_dealt": row.damage_dealt,
                "monster_power": row.monster_power,
                "battle_time": row.battle_time,
                "monster_defeated": bool(row.remaining_health <= 0)
            }
            for row in interactions
        ]
    }
    return response