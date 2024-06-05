from fastapi import APIRouter, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/guild",
    tags=["guild"],
    dependencies=[Depends(auth.get_api_key)],
)

# Model
class Hero(BaseModel):
    '''
    Attributes -
        hero_name: str
            the name of the hero
    '''
    hero_name: str

class Guild(BaseModel):
    '''
    Attributes -
        guild_name: str
            the name of the guild
        player_capacity: int
            how many heroes max that can be recruited by the guild
        gold: int
            how much gold the guild has
    '''
    guild_name: str
    player_capacity: int
    gold: int

# Endpoint

# Create Guild - /world/create_guild/{world_id} (POST)
@router.post("/create_guild/{world_id}")
def create_guild(world_id: int, guild: Guild):
    '''
    Creates a guild at specified world_id\n
    Takes: world_id (int), Guild (guild_name, player_capacity, gold)\n
    Returns: boolean on success or failure of guild creation
    '''

    sql_to_execute = """
    WITH guild_count AS (
        SELECT COUNT(*) AS current_guild_count
        FROM guild
        WHERE world_id = :world_id
    ),
    capacity_check AS (
        SELECT guild_capacity
        FROM world
        WHERE id = :world_id
    )
    INSERT INTO guild (name, player_capacity, gold, world_id)
    SELECT :name, :player_capacity, :gold, :world_id
    FROM guild_count, capacity_check
    WHERE guild_count.current_guild_count < capacity_check.guild_capacity
    RETURNING id
    """
    if world_id < 0:
        raise HTTPException(status_code = 400, detail = "Invalid World Id")
    if guild.player_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Guild Capacity")
    if guild.gold < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Gold")

    with db.engine.begin() as connection:
        try:
            result = connection.execute(sqlalchemy.text(sql_to_execute), {
                "name": guild.guild_name,
                "player_capacity": guild.player_capacity,
                "gold": guild.gold,
                "world_id": world_id
            })
            if result.rowcount > 0:
                return {"success": True, "message": "guild %d created" % result.fetchone().id}
            else:
                return {"success": False, "message": "World %d at max guild capacity" % world_id}
        except sqlalchemy.exc.IntegrityError as http:
            return {"success": False, "message": "Guild name must be unique within specified world %d" % world_id}

# Recruit Hero - /guild/recruit_hero/{guild_id} (POST)
@router.post("/recruit_hero/{guild_id}")
def recruit_hero(guild_id: int, hero: Hero, message: str):
    '''
    Sends out a recruitment request to a hero from a specified guild_id\n
    Takes: guild_id (int), Hero (hero_name)\n
    Returns: boolean on success or failure of recruitment
    '''

    sql_to_execute = sqlalchemy.text(
    """
    WITH insertion AS (
        INSERT INTO recruitment (hero_id, guild_id, status, request_date, notes)
        SELECT id, :guild_id, 'pending', now(), :message
        FROM hero 
        WHERE name = :hero_name AND guild_id IS NULL AND world_id = (SELECT world_id FROM guild WHERE id = :guild_id)
        RETURNING hero_id, (SELECT world_id FROM guild WHERE id = 4)             
    )
    SELECT
        hero.id,
        guild_id,
        hero.world_id as hero_world_id,
        insertion.world_id as guild_world_id
    FROM hero
    LEFT JOIN guild ON guild.id = hero.guild_id
    LEFT JOIN insertion ON insertion.hero_id = hero.id
    WHERE hero.name = :hero_name
    """)
    if hero is None:
        raise HTTPException(status_code = 404, detail = "Hero is not specified")

    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {'hero_name': hero.hero_name, 'guild_id': guild_id, 'message': message})
        if result.rowcount == 0:
            raise HTTPException(status_code = 404, detail = "Hero %s does not exist" % hero.hero_name)
        result = result.one()
        if result.guild_id != None:
            return {"success": False, "message": "Hero already in guild %d" % result.guild_id}
        if result.guild_world_id == None:
            return {"success": False, "message": "Hero is not in proper world_id of guild, Hero located in world %d" % result.hero_world_id}
        return {"success": True}

# Check Available Heroes - /guild/available_heroes/{guild_id} (GET)
@router.get("/available_heroes/{guild_id}")
def available_heroes(guild_id: int):
    '''
    Get query to view all available heroes\n
    Takes: guild_id (int)\n
    Returns: list[Hero]
    '''

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT name, power, health, level
            FROM hero
            WHERE guild_id = :guild_id AND dungeon_id IS NULL
            """), {"guild_id": guild_id}
        )
        heroes = [
            {"hero_name": row.name, "power": row.power, "health": row.health, "level": row.level} 
            for row in result.fetchall()
        ]
    return heroes

# Remove Dead Heroes - /guild/remove_dead_heroes/{guild_id} (POST)
@router.post("/remove_dead_heroes/{guild_id}")
def remove_dead_heroes(guild_id: int, heroes: list[Hero]):
    '''
    Removes dead heroes from a guild\n
    Takes: guild_id (int), list[Hero]\n
    Returns: boolean on success or failure of removals
    Having them list heroes rather than removing all dead heroes gives them time to morn :(
    '''

    hero_names = [hero.hero_name for hero in heroes]
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            DELETE FROM hero
            WHERE name = ANY(:hero_names) AND guild_id = :guild_id AND health <= 0
            """), {"hero_names": hero_names, "guild_id": guild_id}
        )
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "No dead heroes found"}

# Send Party - /guild/send_party/{guild_id} (POST)
@router.post("/send_party/{guild_id}")
def send_party(guild_id: int, party: list[Hero], dungeon_name: str):
    '''
    Sends a party out to a dungeon\n
    Takes: guild_id (int), list[Hero], dungeon_name (TEXT)\n
    Returns: boolean on success or failure
    '''

    # Check if the guild exists
    guild_query = sqlalchemy.text("SELECT * FROM guild WHERE id = :guild_id FOR UPDATE")
    with db.engine.begin() as connection:
        guild = connection.execute(guild_query, {"guild_id": guild_id}).fetchone()
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        
        # Update hero dungeon_id
        hero_names = [hero.hero_name for hero in party]
        update_hero = sqlalchemy.text("""
        WITH updated_heroes AS (
        UPDATE hero
        SET dungeon_id = (SELECT id FROM dungeon WHERE name = :dungeon_name AND status = 'open')
        WHERE name IN :hero_names AND guild_id = :guild_id
        RETURNING dungeon_id
        )
        SELECT updated_heroes.dungeon_id, status
        FROM updated_heroes
        JOIN dungeon ON dungeon.id = updated_heroes.dungeon_id
        """)
        result = connection.execute(update_hero, {"hero_names": tuple(hero_names), "guild_id": guild_id, "dungeon_name": dungeon_name})
            
        if result.rowcount > 0:
            connection.execute(sqlalchemy.text("""
                                            UPDATE dungeon
                                            SET status = 'closed'
                                            WHERE name = :dungeon_name"""),
                                            {"dungeon_name": dungeon_name})
            return {"success": True}
        else:
            raise HTTPException(status_code = 404, detail = "Hero not found or already in a dungeon")

@router.get("/leaderboard")
def get_leaderboard():
    '''
    Get query that returns a leaderboard of the top guilds\n
    Takes:\n
    Returns: json response\n
        - boolean of success or failure\n
        - Leaderboard (rank (int),
                    guild_id (int),
                    guild_name (TEXT),
                    guild_gold (int),
                    hero_count (int),
                    avg_hero_power (float))
    '''

    sql_leaderboard = """
    WITH guild_stats AS (
        SELECT 
            g.id AS guild_id,
            g.name AS guild_name,
            g.gold AS guild_gold,
            COUNT(h.id) AS hero_count,
            COALESCE(AVG(h.power), 0) AS avg_hero_power
        FROM guild g
        LEFT JOIN hero h ON g.id = h.guild_id
        GROUP BY g.id, g.name, g.gold
    ),
    ranked_guilds AS (
        SELECT
            guild_id,
            guild_name,
            guild_gold,
            hero_count,
            avg_hero_power,
            RANK() OVER (ORDER BY guild_gold DESC, avg_hero_power DESC, hero_count DESC) AS rank
        FROM guild_stats
    )
    SELECT *
    FROM ranked_guilds
    ORDER BY rank;
    """
    with db.engine.begin() as connection:
        leaderboard = connection.execute(sqlalchemy.text(sql_leaderboard)).fetchall()

    response = {
        "status": "success",
        "leaderboard": [
            {
                "rank": row.rank,
                "guild_id": row.guild_id,
                "guild_name": row.guild_name,
                "guild_gold": row.guild_gold,
                "hero_count": row.hero_count,
                "avg_hero_power": row.avg_hero_power
            }
            for row in leaderboard
        ]
    }
    return response

