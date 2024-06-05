from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/guild",
    tags=["guild"],
    dependencies=[Depends(auth.get_api_key)],
)

# Models
class Hero(BaseModel):
    hero_name: str

class Guild(BaseModel):
    guild_name: str
    max_capacity: int
    gold: int

class SuccessResponse(BaseModel):
    success: bool
    message: str = None

class HeroDetails(BaseModel):
    hero_name: str
    power: int
    health: int
    level: int

class LeaderboardEntry(BaseModel):
    rank: int
    guild_id: int
    guild_name: str
    guild_gold: int
    hero_count: int
    avg_hero_power: float

class LeaderboardResponse(BaseModel):
    status: str
    leaderboard: list[LeaderboardEntry]

# Endpoints

@router.post("/create_guild/{world_id}", response_model=SuccessResponse)
def create_guild(world_id: int, guild: Guild):
    """
    Create a new guild in the specified world.

    Args:
        world_id (int): The ID of the world where the guild will be created.
        guild (Guild): The details of the guild to be created.

    Returns:
        SuccessResponse: Indicates whether the guild was successfully created.
    """

    if world_id < 0:
        raise HTTPException(status_code = 400, detail = "Invalid World Id")
    if guild.max_capacity < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Guild Capacity")
    if guild.gold < 0:
        raise HTTPException(status_code = 400, detail = "Invalid Gold")

    sql_to_execute = sqlalchemy.text("""
    INSERT INTO guild (name, player_capacity, gold, world_id)
    VALUES (:name, :max_capacity, :gold, :world_id);
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {
            "name": guild.guild_name,
            "max_capacity": guild.max_capacity,
            "gold": guild.gold,
            "world_id": world_id
        })
        if result.rowcount > 0:
            return {"success": True}
        else:
            return {"success": False, "message": "Failed to create guild"}

@router.post("/recruit_hero/{guild_id}", response_model=SuccessResponse)
def recruit_hero(guild_id: int, hero: Hero):
    """
    Recruit a hero to a guild.

    Args:
        guild_id (int): The ID of the guild where the hero will be recruited.
        hero (Hero): The details of the hero to be recruited.

    Returns:
        SuccessResponse: Indicates whether the hero recruitment was successful.
    """

    sql_to_execute = sqlalchemy.text("""
    INSERT INTO recruitment (hero_id, guild_id, status, request_date)
    SELECT id, :guild_id, 'pending', now() 
    FROM hero 
    WHERE name = :hero_name AND guild_id IS NULL AND world_id = (SELECT world_id FROM guild WHERE id = :guild_id);
    """)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {'hero_name': hero.hero_name, 'guild_id': guild_id})
        if result.rowcount > 0:
            return {"success": True}
        else:
            raise HTTPException(status_code = 404, detail = "Hero not found or already in guild")

@router.get("/available_heroes/{guild_id}", response_model=list[HeroDetails])
def available_heroes(guild_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT name, power, health, level
            FROM hero
            WHERE guild_id = :guild_id AND dungeon_id IS NULL
            """), {"guild_id": guild_id}
        )
        heroes = [
            HeroDetails(hero_name=row[0], power=row[1], health=row[2], level=row[3]) 
            for row in result.fetchall()
        ]
    return heroes

@router.post("/remove_heroes/{guild_id}", response_model=SuccessResponse)
def remove_heroes(guild_id: int, heroes: list[Hero]):
    hero_names = [hero.hero_name for hero in heroes]
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            DELETE FROM hero
            WHERE name = ANY(:hero_names) AND guild_id = :guild_id AND health <= 0
            """), {"hero_names": hero_names, "guild_id": guild_id}
        )
        if result.rowcount > 0:
            return SuccessResponse(success=True, message="Dead heroes removed")
        else:
            return SuccessResponse(success=False, message="No dead heroes found")

@router.post("/send_party/{guild_id}", response_model=SuccessResponse)
def send_party(guild_id: int, party: list[Hero], dungeon_name: str):
    # Check if the guild exists
    guild_query = sqlalchemy.text("SELECT * FROM guild WHERE id = :guild_id FOR UPDATE")
    with db.engine.begin() as connection:
        guild = connection.execute(guild_query, {"guild_id": guild_id}).fetchone()
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        
        # Update hero dungeon_id
        hero_names = [hero.hero_name for hero in party]
        update_hero = sqlalchemy.text("""
        UPDATE hero
        SET dungeon_id = (SELECT id FROM dungeon WHERE name = :dungeon_name AND status = 'open')
        WHERE name IN :hero_names AND guild_id = :guild_id
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

@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard():
    """
    Get the guild leaderboard.

    Returns:
        LeaderboardResponse: The current leaderboard with guild rankings.
    """
    
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

    return LeaderboardResponse(
        status="success",
        leaderboard=[
            LeaderboardEntry(
                rank=row.rank,
                guild_id=row.guild_id,
                guild_name=row.guild_name,
                guild_gold=row.guild_gold,
                hero_count=row.hero_count,
                avg_hero_power=row.avg_hero_power
            )
            for row in leaderboard
        ]
    )
