# API Specification for Arthur's Last Crusade

## 1. Guilds and Recruiting
The API calls are made in this sequence when creating a guild and recruiting some heroes.

1. `Create Guild`
2. `View Heroes`
3. `Recruit Hero`

### 1.1 Create Guild - `/world/create_guild/` (POST)
Creates a guild in the world. The guild may be denied from being created if there is some details match another existing guild.
**Request**:
```json
[
    {
        "rank" : "number",
        "guild_name": "string",
        "max_capacity": "number",
        "gold": "number",
    }
]
```
***Response***:
```json
{
    "success": "boolean"
}
```

### 1.2 View Heroes - `/world/view_heroes/` (GET)
Shares all the available heroes in the world.
**Response**:
```json
[
    {
        "hero_name":"string",
        "level":"number",
        "power":"number",
        "age":"number",
        "cost":"number"
    }
]
```

### 1.3 Recruit Hero - `/guild/recruit_hero/{hero_id}/` (POST)
Recruits a hero.
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

### 2.1 Create Dungeon - `/dungeon/create_dungeon/` (POST)
Creates a dungeon in the world. Errors if there is a dungeon with the same name.
**Request**:
```json
[
    {
        "dungeon_name": "string",
        "dungeon_size": "number",
        "dungeon_level": "number",
        "reward": "number",
    }
]
```
***Response***:
```json
{
    "success": "boolean"
}
```



### 2.2 Create Monster - `/dungeon/create_monster/` (POST)
Creates a monster within a dungeon.
**Request**:
```json
[
    {
        "level" : "number",
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
2. `Send Party`
3. `Collect Bounty`
4. `Assess Damage`

### 3.1 Get Quests - `/world/get_quests/` (GET)
Shares all the available dungeons to be raided in the world
**Response**:
```json
[
    {
        "dungeon_name": "string",
        "level": "number",
    }
]
```

### 3.2 Send Party - `/dungeon/send_party/` (POST)
Sends the party (list of heroes) to be sent to the dungeon. The party may be sent back if they do not meet the level requirements or their party size does not meet the dungeon size.
**Request**:
```json
[
    {
        "hero_name": "string",
        "level": "number",
        "power": "number",
        "age": "number",
    }
]
```
***Response***:
```json
{
    "success": "boolean"
}
```

### 3.3 Collect Bounty - `/dungeon/collect_bounty/` (GET)
Collects the gold alloted for the guild from the dungeon raid
***Response***:
```json
{
    "gold": "number"
}
```

### 3.4 Assess Damage - `/dungeon/assess_damage/` (GET)
Gets a list of heroes that died in action from the raid
***Response***:
```json
[
    {
        "hero_name": "string",
        "level": "number",
        "power": "number",
        "age": "number",
    }
]
```

## 4. Heroes in Dungeons
API calls are made in this sequence when it comes to fighting dungeons.

## 5. Heroes
API calls are made in this sequence for heroes in the world and outside dungeons. 

1. `Create Hero`
2. `Age Hero`
3. `Raise Level`

If the heroes are not yet in a guild, they will call the below as well.

4. `View Pending Requests`
5. `Accept Request`

### 5.1 Create Hero - `/world/create_hero/` (POST)
**Request**:
```json
[
    {
        "name" : "string",
        "class": "string",
        "level": "number",
        "age": "number",
    }
]
```
***Response***:
```json
{
    "success": "boolean"
}
```
### 5.2 Age Hero - `/world/age_hero/{hero_id}` (POST)
***Response***:
```json
{
    "success": "boolean"
}
```
### 5.3 Raise Level - `/hero/raise_level/{hero_id}` (POST)
***Response***:
```json
{
    "success": "boolean"
}
```
### 5.4 View Pending Requests - `/hero/view_pending_requests/{hero_id}` (GET)
***Response***:
```json
{
    [
        "guild_name":"string",
        "rank":"number",
        "gold":"number"
    ]
}
```
### 5.5 Accept Request - `/world/accept_request/{guild_id}` (POST)
```json
{
    "success": "boolean"
}
```