# API Specification for Arthur's Last Crusade

## 1. Guilds and Recruiting
The API calls are made in this sequence when creating a guild and recruiting some heroes.

1. `Create Guild`
2. `View Heroes`
3. `Recruit Hero`

### 1.1 Create Guild - `/guild/create_guild/{world_id}` (POST)
Creates a guild in the world. The guild may be denied from being created if there is some details match another existing guild.

**Request**:
```json
[
    {
        "guild_name": "string",
        "max_capacity": "int",
        "gold": "int",
    }
]
```
***Response***:

```json
{
    "success": "boolean"
}
```

### 1.2 View Heroes - `/world/view_heroes/{world_id}` (GET)
Shares all the available heroes in the world.

**Response**:
```json
[
    {
        "hero_name":"string",
        "level":"int",
        "power":"int",
        "age":"int",
        "cost":"int"
    }
]
```

### 1.3 Recruit Hero - `/guild/recruit_hero/{guild_id}` (POST)
Recruits a hero.

***Request***:
```json
{
    "hero_name" : "string"
}
```

***Response***:
```json
{
    "success": "boolean"
}
```

## 2. Dungeon Generation
API calls are made in this sequence when creating a dungeon.
1. `Create Dungeon`
2. `Create Monster`

### 2.1 Create Dungeon - `/dungeon/create_dungeon/{world_id}` (POST)
Creates a dungeon in the world. Errors if there is a dungeon with the same name.

**Request**:
```json
[
    {
        "dungeon_name": "string",
        "player_capacity": "int",
        "monster_capacity":"int",
        "dungeon_level": "int",
        "reward": "int",
    }
]
```

***Response***:
```json
{
    "success": "boolean"
}
```

### 2.2 Create Monster - `/dungeon/create_monster/{dungeon_id}` (POST)
Creates a monster within a dungeon.

**Request**:
```json
[
    {
        "type" : "string",
    }
]
```

***Response***:
```json
{
    "success": "boolean"
}
```

## 3. Quests
API calls are made in this sequence when it comes to sending heroes out into dungeons.

1. `Get Quests`
2. `Check Available Heroes`
3. `Send Party`
4. `Collect Bounty`
5. `Assess Damage`
6. `Remove Dead Heroes`

### 3.1 Get Quests - `/world/get_quests/{world_id}` (GET)
Shares all the available dungeons to be raided in the world

**Response**:

```json
[
    {
        "dungeon_name": "string",
        "level": "int",
    }
]
```

### 3.2 Check Available Heroes - `/guild/available_heroes/{guild_id}` (GET)
Shares all available heroes in the guild

***Response***:
```json
[
    {
        "hero_name": "string",
        "level": "int",
        "power": "int",
        "age": "int",
    }
]
```

### 3.3 Send Party - `/guild/send_party/{guild_id}` (POST)
Sends the party (list of heroes) to be sent to the dungeon. The party may be sent back if they do not meet the level requirements or their party size does not meet the dungeon size.

**Request**:
```json
[
    {
        "hero_name": "string"
    }
]

"dungeon_name": "string"
```
***Response***:

```json
{
    "success": "boolean"
}
```

### 3.4 Collect Bounty - `/dungeon/collect_bounty/{guild_id}` (POST)
Collects the gold alloted for the guild from the dungeon raid

***Response***:

```json
{
    "gold": "int"
}
```

### 3.5 Assess Damage - `/dungeon/assess_damage/{dungeon_id}` (GET)
Gets a list of heroes that died in action from the raid

***Response***:

```json
[
    {
        "hero_name": "string",
        "level": "int",
        "power": "int",
        "age": "int",
    }
]
```

### 3.6 Remove Dead Heroes - `/guild/remove_dead_heroes/{guild_id}` (POST)
Removes dead heroes from the guild

**Request**:

```json
[
    {
        "hero_name":"string"
    }
]
```

***Response***:

```json
{
    "success": "boolean"
}
```

## 4. Heroes
API calls are made in this sequence for heroes in the world and outside dungeons. 

1. `Create Hero`
2. `Age Hero`
3. `Check XP`
4. `Raise Level`

If the heroes are not yet in a guild, they will call the below as well.

5. `View Pending Requests`
6. `Accept Request`

### 4.1 Create Hero - `/world/create_hero/{world_id}` (POST)

**Request**:

```json
[
    {
        "name" : "string",
        "role": "string",
        "level": "int",
        "age": "int",
    }
]
```

***Response***:

```json
{
    "success": "boolean"
}
```
### 4.2 Age Hero - `/world/age_hero/{hero_id}` (POST)

***Response***:
```json
{
    "success": "boolean"
}
```
### 4.3 Check XP - `/hero/check_xp/{hero_id}` (GET)

***Response***:
```json
{
    "xp": "int"
}
```
### 4.4 Raise Level - `/hero/raise_level/{hero_id}` (POST)

***Response***:
```json
{
    "success": "boolean"
}
```
### 4.5 View Pending Requests - `/hero/view_pending_requests/{hero_id}` (GET)

***Response***:
```json
[
    {
        "guild_name":"string",
        "rank":"int",
        "gold":"int" 
    }
]
```
### 4.6 Accept Request - /hero/accept_request/{hero_id}/ (POST)

***Request***:
```json
{
    "guild_name": "string"
}
```
***Response***:
```json
{
    "success": "boolean"
}
```

## 5. Heroes in Dungeons
API calls are made in this sequence when it comes to fighting dungeons.

1. `Find Monsters`
2. `Attack Monster`

Heroes may periodically check their health and choose to run away

3. `Check Health`
4. `Run Away`

This may occur if a hero runs out of health.

5. `Die`

### 5.1 Find Monsters - `/hero/find_monsters/{dungeon_id}/` (GET)

**Response**:
```json
[
    {
        "id":"int",
        "name" : "string",
        "level": "int",
        "power": "int",
    }
]
```
### 5.2 Attack Monster - `/hero/attack_monster/{hero_id}/` (POST)

**Request**:
```json
{
    "monster_id":"int",
}
```

**Response**:
```json
{
    "success": "boolean"
}
```

### 5.3 Check Health - `/hero/check_health/{hero_id}/` (GET)

**Response**:
```json
{
    "health": "int"
}
```
### 5.4 Run Away - `/hero/run_away/{hero_id}/` (POST)

**Response**:
```json
{
    "success": "boolean"
}
```
### 5.5 Die - `/hero/die/{hero_id}/` (POST)

**Response**:
```json
{
    "success": "boolean"
}
```

## 6. Monsters
API calls are made in this sequence when it comes to monsters attacking heroes.

1. `Find Heroes`
2. `Attack Hero`

This can occur if a monster is killed by a hero.

3. `Die`

### 6.1 Find Heroes - `/monster/find_heroes/{dungeon_id}/` (GET)

**Response**:
```json
[
    {
        "id":"int",
        "name" : "string",
        "level": "int",
        "power": "int",
    }
]
```

### 6.2 Attack Hero - `/monster/attack_hero/{monster_id}/` (POST)

**Request**:
```json
{
    "hero_id":"int",
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

### 6.3 Die - `/monster/die/{monster_id}` (POST)

**Response**:

```json
{
    "success": "boolean"
}
```

## 7. Complex Endpoints
Complex meaning it does significantly more than just a straightforward create/update/delete/read from the database.

### 7.1 Hero-Monster Interaction Report - `/hero/{hero_id}/monster_interactions` (GET)
Provides detailed insights into a hero's interactions with monsters, including metrics such as the number of monsters defeated, total damage dealt, and detailed statistics for each battle.

**Response**:
```json
{
    "status": "boolean",
    "hero_id": "int",
    "total_battles": "int",
    "monsters_defeated": "int",
    "total_damage_dealt": "int",
    "battle_details": [
        {
            "monster_id": "int",
            "monster_type": "string",
            "monster_level": "int",
            "initial_health": "int",
            "remaining_health": "int",
            "damage_dealt": "int",
            "monster_power": "int",
            "battle_time": "timestamp",
            "monster_defeated": "boolean"
        }
    ]
}


### 7.2 Leaderboard - `/leaderboard` (GET)
Provides a leaderboard ranking guilds based on their total gold, the number of heroes, and the average power of their heroes.

**Response**:
```json
{
    "status": "boolean",
    "leaderboard": [
        {
            "rank": "int",
            "guild_id": "int",
            "guild_name": "string",
            "guild_gold": "int",
            "hero_count": "int",
            "avg_hero_power": "int"
        }
    ]
}