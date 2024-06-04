# Performance Testing Results

## Fake Data Modeling

Rows for each table:

1. Worlds: 150
2. Guilds: 25000
3. Dungeons: 100000
4. Monsters: 300000
5. Heroes: 600000
6. Targetings: 100000

Our service would probably scale somewhat like this since we don't expect the number of worlds to be that many compared to the others. For example, thinking of a well-known game like World of Warcraft, there are only 255 active servers, and that is a game with millions of players. We expect the guilds table to have the second least as we expect that there would be multiple heroes in a guild. We expect there to be a lot of dungeons, monsters, and heroes however which should make up most of the rows. We expect the targeting table to have a lot as well.

## Performance results of hitting endpoints

### World Endpoints
- **View Heroes**
  - **GET** `/world/view_heroes/{world_id}` - 149.76 ms
- **Get Quests**
  - **GET** `/world/get_quests/{world_id}`
- **Create Hero**
  - **POST** `/world/create_hero/{world_id}`
- **Age Hero**
  - **POST** `/world/age_hero/{hero_id}`

### Dungeon Endpoints
- **Create Dungeon**
  - **POST** `/dungeon/create_dungeon/{world_id}`
- **Create Monster**
  - **POST** `/dungeon/create_monster/{dungeon_id}`
- **Collect Bounty**
  - **POST** `/dungeon/collect_bounty/{guild_id}`
- **Assess Damage**
  - **GET** `/dungeon/assess_damage/{dungeon_id}`

### Hero Endpoints
- **Check XP**
  - **GET** `/hero/check_xp/{hero_id}`
- **Raise Level**
  - **POST** `/hero/raise_level/{hero_id}`
- **View Pending Requests**
  - **GET** `/hero/view_pending_requests/{hero_id}`
- **Accept Request**
  - **POST** `/hero/accept_request/{hero_id}`
- **Attack Monster**
  - **POST** `/hero/attack_monster/{hero_id}`
- **Check Health**
  - **GET** `/hero/check_health/{hero_id}`
- **Run Away**
  - **POST** `/hero/run_away/{hero_id}`
- **Die**
  - **POST** `/hero/die/{hero_id}`
- **Find Monsters**
  - **GET** `/hero/find_monsters/{dungeon_id}`
- **Hero Monster Interactions**
  - **GET** `/hero/{hero_id}/monster_interactions`

### Monster Endpoints
- **Find Heroes**
  - **GET** `/monster/find_heroes/{dungeon_id}`
- **Attack Hero**
  - **POST** `/monster/attack_hero/{monster_id}`
- **Die**
  - **POST** `/monster/die/{monster_id}`

### Guild Endpoints
- **Create Guild**
  - **POST** `/guild/create_guild/{world_id}`
- **Recruit Hero**
  - **POST** `/guild/recruit_hero/{guild_id}` - 6.37 ms
- **Available Heroes**
  - **GET** `/guild/available_heroes/{guild_id}`
- **Remove Heroes**
  - **POST** `/guild/remove_heroes/{guild_id}`
- **Send Party**
  - **POST** `/guild/send_party/{guild_id}`
- **Get Leaderboard**
  - **GET** `/guild/leaderboard`

## Performance tuning