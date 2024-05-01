# Example Flows

## 1. Recruiting a Hero to Guild Example Flow
Mages Only wants to recruit a new hero into their guild because they need more power to clear the dungeons. First, they check the entire world of heroes by `GET /world/view_heroes/`. Mages Only sees that Elminster the Sage is not currently in a guild and that they had enough gold to recruit him. Mages Only wants to recruit Elminster the Sage because he's super powerful and having him would definitely increase their guild rank and gold. 

Mages Only then makes a request to Elminster the Sage.

To do so:
- Mages Only then sends a request to Elminster the Sage by calling `POST /guild/recruit_hero/{hero_id}/`
- Elminster the Sage calls `GET /hero/view_pending_requests/{hero_id}` one day because he is not in a guild. He sees the request from Mages Only.
- Elminster the Sage then has the option to accept by calling `POST /hero/accept_request/{guild_id}/`

Elminster the Sage accepts Mages Only and now he can join them in the dungeons.

## 2. Sending a Party to a Dungeon and Collecting Bounty
Mages Only wants to send a party to a dungeon to raise their gold and rank. First they need to check all the available dungeons currently by `GET /world/get_quests/`. Mages Only sees that there is a dungeon called "Watcher's Keep" with a dungeon level of 27 and can take a capacity of 5 heroes. 

Mages Only believes they have heroes strong enough to clear the dungeon, so they go send a party.
- starts by calling `GET /guild/available_heroes/{guild_id}` and passes their guild id
- they find five available heroes that seem like they can clear the dungeon and call `POST /dungeon/send_party/{dungeon_id}` passing in the dungeon id of "Watcher's Keep"
- let's say after some time, the dungeon is cleared (see Example Flow #3), then the guild can call `POST /dungeon/collect_bounty/{guild_id}` to collect their reward
- Mages Only also needs to find out whether any hero died after the dungeon, so they call `GET /dungeon/assess_damage/{dungeon_id}`
- they learn that Bob the Mage and Sarah the Sorceress died, so they remove them by calling `/guild/remove_heroes/{guild_id}` passing in those two heroes

Now, Mages Only can continue sending more heroes out to clear dungeons and rake in some gold.

## 3. Party Fights and Clears a Dungeon
The party sent out by Mages Only consists of the unit Alexander the Knight, Walker the Monk, Yowl the Barbarian, Bob the Mage, and Sarah the Sorceress. As the heroes enter the dungeon… they must first search for monsters, so they call `GET /dungeon/find_monsters/{dungeon_id}/`

All the heroes choose to remain.
- the heroes individually一after evaluating the threat一can choose to run away, by calling `POST /hero/run_away/{hero_id}/`
- then the monsters and heroes break out into 1 on 1 battles, with monsters or heroes waiting in queue for an opening to attack. Monster at the top of the queue will call `GET /monster/find_heroes/{dungoen_id}/` to choose a hero in the queue to attack.
- fights proceed at the same time, where hero calls on `POST /hero/attack_monster/{hero_id}/` to attack monster, and monsters call on `POST /monster/attack_hero/{monster_id}/` to attack hero.
- let’s say Yowl the Barbarian kills the monster “Madam Tongue Eater” assigned to him, “Madam Tongue Eater” calls `GET /monster/die/{monster_id}` and the next monster from the top of the queue will be assigned to Yowl.
- Yowl decides to call `POST /hero/run_away/{hero_id}/` before a monster is assigned to him however, and successfully escapes.
- at the same time, Sarah the Sorceress was just killed by “Small Pink Slime” and so Sarah the Sorceress issues the call `GET /hero/die/{hero_id}/` and “Small Pink Slime" goes back into the queue.
- after some gruesome combat, the heroes come out on top, with Bob the Mage and Sarah the Sorceress sadly passing away.
- all remaining heroes (cowards and victors alike) check their xp level with the call `POST /hero/check_xp/{hero_id}`, and, if large enough, call `POST /hero/raise_level/{hero_id}`
- they come back home triumphantly and crossing their fingers that the guild does not check up on them so they can keep all the gold for themselves.
