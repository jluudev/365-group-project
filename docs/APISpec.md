# API Specification for Arthur's Last Crusade

## 1. Guilds and Recruiting
The API calls are made in this sequence when creating a guild and recruiting some heroes.

1. `Create Guild`
2. `View Heroes`
3. `Recruit Hero`

### 1.1 Create Guild - `/guild/create_guild/` (POST)
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

## 2. Dungeons:
API calls are made in this sequence when it comes to fighting dungeons.




