## 2. Sending a Party to a Dungeon and Collecting Bounty
Mages Only wants to send a party to a dungeon to raise their gold and rank. First they need to check all the available dungeons currently by `GET /world/get_quests/{world_id}`. Mages Only sees that there is a dungeon called "The Grave of a Wrecked Ship".

Mages Only believes they have heroes strong enough to clear the dungeon, so they go send a party.
- starts by calling `GET /guild/available_heroes/{guild_id}` and passes their guild id
- they find three available heroes that seem like they can clear the dungeon and call `POST /guild/send_party/{guild_id}` passing in the dungeon name of "Watcher's Keep" as well as the party of heroes.
- let's say after some time, the dungeon is cleared (see Example Flow #3), then the guild can call `POST /dungeon/collect_bounty/{guild_id}` to collect their reward
- Mages Only also needs to find out whether any hero died after the dungeon, so they call `GET /dungeon/assess_damage/{dungeon_id}`
- they learn that Wizard101 died, so they remove them by calling `POST /guild/remove_heroes/{guild_id}` passing in the heroes

Now, Mages Only can continue sending more heroes out to clear dungeons and rake in some gold.

### Testing Results for Flow #2
1. `GET /world/get_quests/{world_id}`

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/world/get_quests/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
[
  {
    "dungeon_name": "The Grave of a Wrecked Ship",
    "level": 5
  }
]
```

2. `GET /guild/available_heroes/{guild_id}`

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/guild/available_heroes/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
[
  {
    "hero_name": "Wizard101",
    "power": 10,
    "health": 50,
    "level": 1
  },
  {
    "hero_name": "Sorceress123",
    "power": 10,
    "health": 50,
    "level": 5
  },
  {
    "hero_name": "Charlotte",
    "power": 10,
    "health": 50,
    "level": 10
  }
]
```

3. `POST /guild/send_party/{guild_id}`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/guild/send_party/1?dungeon_name=The%20Grave%20of%20a%20Wrecked%20Ship' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "hero_name": "Wizard101"
  },
{
    "hero_name": "Sorceress123"
  },
{
    "hero_name": "Charlotte"
  }

]'
```

Response body:
```json
{
  "success": true
}
```

4. `POST /dungeon/collect_bounty/{guild_id}`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/dungeon/collect_bounty/1?dungeon_id=7' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "gold": 350
}
```

5. `GET /dungeon/assess_damage/{dungeon_id}`

- note for this test, we manually changed the health of someone to 0, since fighting is part of the next flow

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/dungeon/assess_damage/7?guild_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
[
  {
    "hero_name": "Wizard101",
    "level": 1,
    "power": 10,
    "health": 0
  }
]
```

6. `POST /guild/remove_heroes/{guild_id}`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/guild/remove_heroes/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "hero_name": "Wizard101"
  }
]'
```

Response body:
```json
{
  "success": true
}
```

## 3. Party Fights and Clears a Dungeon
The party sent out by Mages Only consists of some heroes to Gold Beach. As the heroes enter the dungeon… they must first search for monsters, so they call `GET /hero/find_monsters/{dungeon_id}/`

All the heroes choose to remain.
- the heroes individually一after evaluating the threat一can choose to run away, by calling `POST /hero/run_away/{hero_id}/`
- then the monsters and heroes break out into 1 on 1 battles, with monsters or heroes waiting in queue for an opening to attack. Monster at the top of the queue will call `GET /monster/find_heroes/{dungeon_id}/` to choose a hero in the queue to attack.
- fights proceed at the same time, where hero calls on `POST /hero/attack_monster/{hero_id}/` to attack monster, and monsters call on `POST /monster/attack_hero/{monster_id}/` to attack hero.
- let’s say Yowl the Barbarian kills the monster “Madam Tongue Eater” assigned to him, “Madam Tongue Eater” calls `POST /monster/die/{monster_id}` and the next monster from the top of the queue will be assigned to Yowl.
- A different hero, Amelia, decides to call `POST /hero/run_away/{hero_id}/` before a monster is assigned to her, and successfully escapes.
- at the same time, Sarah the Sorceress was just killed by “Small Pink Slime” and so Sarah the Sorceress issues the call `POST /hero/die/{hero_id}/` and “Small Pink Slime" goes back into the queue.
- after some gruesome combat, the heroes come out on top, with Bob the Mage and Sarah the Sorceress sadly passing away.
- all remaining heroes (cowards and victors alike) check their xp level with the call `GET /hero/check_xp/{hero_id}`, and, if large enough, call `POST /hero/raise_level/{hero_id}`
- they come back home triumphantly and crossing their fingers that the guild does not check up on them so they can keep all the gold for themselves.

### Testing Results for Flow #3

1. `GET /hero/find_monsters/{dungeon_id}/`

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/hero/find_monsters/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
[
  {
    "id": 1,
    "name": "Coconut Slime",
    "level": 4,
    "health": 10,
    "power": 3
  },
  {
    "id": 2,
    "name": "Coconut Slime",
    "level": 5,
    "health": 11,
    "power": 4
  },
  {
    "id": 3,
    "name": "Coconut Slime",
    "level": 4,
    "health": 10,
    "power": 3
  },
  {
    "id": 4,
    "name": "Coconut Slime",
    "level": 5,
    "health": 11,
    "power": 4
  },
  {
    "id": 5,
    "name": "Coconut Slime",
    "level": 4,
    "health": 10,
    "power": 3
  },
  {
    "id": 6,
    "name": "Coconut Slime",
    "level": 4,
    "health": 10,
    "power": 3
  },
  {
    "id": 7,
    "name": "Coconut Slime",
    "level": 5,
    "health": 11,
    "power": 4
  },
  {
    "id": 8,
    "name": "Coconut Slime",
    "level": 4,
    "health": 10,
    "power": 3
  },
  {
    "id": 20,
    "name": "Cyclops",
    "level": 13,
    "health": 80,
    "power": 35
  }
]
```

2. `GET /monster/find_heroes/{dungeon_id}/`

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/monster/find_heroes/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
[
  {
    "id": 24,
    "name": "Harper",
    "level": 10,
    "power": 10
  },
  {
    "id": 25,
    "name": "Scarlett",
    "level": 10,
    "power": 10
  },
  {
    "id": 26,
    "name": "Aurora",
    "level": 10,
    "power": 10
  },
  {
    "id": 27,
    "name": "Aria",
    "level": 10,
    "power": 10
  },
  {
    "id": 28,
    "name": "Amelia",
    "level": 10,
    "power": 10
  }
]
```

3. `POST /hero/attack_monster/{hero_id}/`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/hero/attack_monster/24?monster_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "success": "OK"
}
```


4. `POST /monster/attack_hero/{monster_id}/`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/monster/attack_hero/2?hero_id=24' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "success": true
}
```

5. `POST /monster/die/{monster_id}`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/monster/die/1' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934'
```

Response body:
```json
{
  "success": true
}
```

6. `POST /hero/run_away/{hero_id}/`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/hero/run_away/28' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "success": true
}
```

7. `POST /hero/die/{hero_id}/`
- Note, we manually modified a hero's health to 0, but you can repeatedly call attack_hero to make the  health 0 too.

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/hero/die/27' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "success": true
}
```

7. `GET /hero/check_xp/{hero_id}`

```
curl -X 'GET' \
  'https://arthurslastcrusade.onrender.com/hero/check_xp/28' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "xp": 100
}
```


8. `POST /hero/raise_level/{hero_id}`

```
curl -X 'POST' \
  'https://arthurslastcrusade.onrender.com/hero/raise_level/28' \
  -H 'accept: application/json' \
  -H 'access_token: 4888d45f8ecd9127e7b5aef96fb5f934' \
  -d ''
```

Response body:
```json
{
  "success": true
}
```
