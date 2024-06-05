Code Review and Schema/API fixes
- made consistent error handling in guild/send_party
- Added age and class to hero table
- added docstrings to all function endpoints and class declarations
- changed accessing of find_heroes' hero data to column selection rather than indexing
- remove_heroes renamed to remove_dead_heroes to be more reflective of function's purpose
- APISpec.md has been updated for current endpoints
- removed monster/die and hero/die from endpoints, it is easier to just check if health == 0
- standardized response of dungeon/collect_bounty endpoint
- the following endpoints have been updated to reflect more informative success and failure messages
    - guild/create_guild
    - dungeon/create_dungeon
    - world/create_hero
    - dungeon/create_monster
    - hero/raise_level
    - guild/recruit_hero
    - monster/find_heroes
    - hero/check_health
- schema now has enums for the status field in recruitment and dungeon tables
- moved update_hero query out of a for loop in guild/send_party

Recommendations that were ignored
- You could create more helper functions to simplify the longer functions in your code.
    I would say our problem is not that there is anything super complex in our functions, more that there are a lot of operations involving gets and sets that need to interact nicely.
- view_pending_requests in hero.py, consider implementing pagination to limit the amount of data returned with each request/improve overall scalability
    No need because there will only be a number of requests less than or equal to the number of guilds in the world, which is not that many.
- Use consistent method of querying: either query builder or raw SQL. 
    The process of using a consistent method of querying is enforced by larger companies because there is a constant rotation of new workers and a large body working on the code. It is necessary for larger companies because otherwise there is too much time spent understanding code. For a working group of 4 people, it wastes more time trying to coordinate a consistent method of querying.
- Add a foreign key constraint to link monsters to specific dungeons they belong to.
    I think we already had this? But if not we definitely do at this point. :D
- Add a table to track hero participation in quests/dungeons, recording information such as start/end times and quest completion status.
    This one seems like an additional feature rather than for bug and implementation fixing.
- Add a table to define different reward tiers for dungeons, allowing for customizable rewards based on dungeon difficulty or level.
    I don’t see the point in creating an additional table that would hold one value, that is then referenced by an id… other than limiting the possible reward options that can be given for the dungeon. They could very well be referring to creating a new function that evaluates the difficulty of the dungeon and then assigns the reward, which is nifty, but overall an additional feature that trades convenience for less creativity.
- Keep a consistent type for integer values (e.g. don't mix int8 and int4).
    All id’s specified in the db are set to BIGINT, or int8. The requirement to have data set to one specific data type is to keep things simpler and safer for code integration. As of right now, supabase defaulted to BIGINT for primary keys, which also means all of our foreign keys are BIGINT. As long as we keep in mind this discrepancy, I don’t see any issue in keeping the distinction.
- Replace null with default values (e.g. if a guild_id foreign does not exist for a record in hero, set it to -1 instead).
    Does not make a difference? All that changes is we check for -1 instead of None?
- Consider adding a **foreign key ** to the monsters table (world_id) which refers to the primary key id in worlds table. I would imagine that monsters are associated with a world.
    Monsters reside solely in the dungeons they are created in, they would only need to have a foreign key to world if the monsters were to move dungeons and are restricted to their world_id; heroes have a foreign key to world because they are able to be recruited to different guilds, thus world_id needs to be checked.
- Generally, there should be constraints on levels. Currently, you set level to a default value of 1 and increase over time. I would imagine there should be a maximum level. Set this as an upper constraint in the schema!
    While this is a good idea, I think the idea delves more into personal preference rather than functionality [if we ignore levels surpassing the int limit that is] and for this project I think it would be more fun to allow every increasing levels for limitless growth and the endless desire for our players to become enthralled and brainwashed by our game to play forever, always increasing their level. Also adding level limits introduces the complexity of having to include logarithmic leveling, which is beyond this current implementation.
- Rename 20240501223238_schema.sql to schema.sql and place it in a more accessible location. 
    The numbers prior to schema are for dating purposes, renaming the schema does not improve performance and schema.sql has to be in the supabase folder to run the supabase, We can make a copy of the schema.sql and place it in docs folder for convenience.