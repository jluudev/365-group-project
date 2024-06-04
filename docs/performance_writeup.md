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
  - **GET** `/world/get_quests/{world_id}` - 55.37 ms
- **Create Hero**
  - **POST** `/world/create_hero/{world_id}` - 3.45 ms
- **Age Hero**
  - **POST** `/world/age_hero/{hero_id}` - 9.32 ms

### Dungeon Endpoints
- **Create Dungeon**
  - **POST** `/dungeon/create_dungeon/{world_id}` - 3.08 ms
- **Create Monster**
  - **POST** `/dungeon/create_monster/{dungeon_id}` - 3.06 ms
- **Collect Bounty**
  - **POST** `/dungeon/collect_bounty/{guild_id}`
- **Assess Damage**
  - **GET** `/dungeon/assess_damage/{dungeon_id}`

### Hero Endpoints
- **Check XP**
  - **GET** `/hero/check_xp/{hero_id}` - 2.62 ms
- **Raise Level**
  - **POST** `/hero/raise_level/{hero_id}` - 2.68 ms
- **View Pending Requests**
  - **GET** `/hero/view_pending_requests/{hero_id}`
- **Accept Request**
  - **POST** `/hero/accept_request/{hero_id}`
- **Attack Monster**
  - **POST** `/hero/attack_monster/{hero_id}` - 8.43 ms
- **Check Health**
  - **GET** `/hero/check_health/{hero_id}` - 3.14 ms
- **Run Away**
  - **POST** `/hero/run_away/{hero_id}` - 5.33 ms
- **Die**
  - **POST** `/hero/die/{hero_id}` - 6.01 ms
- **Find Monsters**
  - **GET** `/hero/find_monsters/{dungeon_id}` - 82.23 ms
- **Hero Monster Interactions**
  - **GET** `/hero/{hero_id}/monster_interactions` - 5.47 ms

### Monster Endpoints
- **Find Heroes**
  - **GET** `/monster/find_heroes/{dungeon_id}` - 22.93 ms
- **Attack Hero**
  - **POST** `/monster/attack_hero/{monster_id}` - 4.09 ms
- **Die**
  - **POST** `/monster/die/{monster_id}` - 3.65 ms

### Guild Endpoints
- **Create Guild**
  - **POST** `/guild/create_guild/{world_id}` - 3.41 ms
- **Recruit Hero**
  - **POST** `/guild/recruit_hero/{guild_id}` - 6.37 ms
- **Available Heroes**
  - **GET** `/guild/available_heroes/{guild_id}`
- **Remove Heroes**
  - **POST** `/guild/remove_heroes/{guild_id}`
- **Send Party**
  - **POST** `/guild/send_party/{guild_id}`
- **Get Leaderboard**
  - **GET** `/guild/leaderboard` - 497.23 ms

## Performance tuning
- **Get Leaderboard**
  - **GET** `/guild/leaderboard` - 497.23 ms

| QUERY PLAN                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sort  (cost=26087.12..26149.62 rows=25000 width=78) (actual time=490.267..491.039 rows=25003 loops=1)                                                |
|   Sort Key: (rank() OVER (?))                                                                                                                        |
|   Sort Method: quicksort  Memory: 3309kB                                                                                                             |
|   ->  WindowAgg  (cost=23448.42..24010.92 rows=25000 width=78) (actual time=478.493..486.099 rows=25003 loops=1)                                     |
|         ->  Sort  (cost=23448.42..23510.92 rows=25000 width=70) (actual time=478.471..479.620 rows=25003 loops=1)                                    |
|               Sort Key: guild_stats.guild_gold DESC, guild_stats.avg_hero_power DESC, guild_stats.hero_count DESC                                    |
|               Sort Method: quicksort  Memory: 3211kB                                                                                                 |
|               ->  Subquery Scan on guild_stats  (cost=21059.71..21622.21 rows=25000 width=70) (actual time=461.825..469.694 rows=25003 loops=1)      |
|                     ->  HashAggregate  (cost=21059.71..21372.21 rows=25000 width=70) (actual time=461.824..468.199 rows=25003 loops=1)               |
|                           Group Key: g.id                                                                                                            |
|                           Batches: 1  Memory Usage: 5905kB                                                                                           |
|                           ->  Hash Right Join  (cost=791.50..16559.71 rows=600000 width=42) (actual time=11.764..358.303 rows=479885 loops=1)        |
|                                 Hash Cond: (h.guild_id = g.id)                                                                                       |
|                                 ->  Seq Scan on hero h  (cost=0.00..14193.00 rows=600000 width=20) (actual time=0.251..97.903 rows=600008 loops=1)   |
|                                 ->  Hash  (cost=479.00..479.00 rows=25000 width=30) (actual time=11.450..11.451 rows=25003 loops=1)                  |
|                                       Buckets: 32768  Batches: 1  Memory Usage: 1831kB                                                               |
|                                       ->  Seq Scan on guild g  (cost=0.00..479.00 rows=25000 width=30) (actual time=0.050..9.018 rows=25003 loops=1) |
| Planning Time: 8.184 ms                                                                                                                              |
| Execution Time: 492.657 ms                                                                                                                           |
### Add Index
`CREATE INDEX ON hero (guild_id);`
`CREATE INDEX ON guild (id);`

| QUERY PLAN                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sort  (cost=26088.00..26150.50 rows=25003 width=78) (actual time=218.027..218.755 rows=25003 loops=1)                                                |
|   Sort Key: (rank() OVER (?))                                                                                                                        |
|   Sort Method: quicksort  Memory: 3309kB                                                                                                             |
|   ->  WindowAgg  (cost=23448.95..24011.52 rows=25003 width=78) (actual time=208.193..215.108 rows=25003 loops=1)                                     |
|         ->  Sort  (cost=23448.95..23511.46 rows=25003 width=70) (actual time=208.174..209.119 rows=25003 loops=1)                                    |
|               Sort Key: guild_stats.guild_gold DESC, guild_stats.avg_hero_power DESC, guild_stats.hero_count DESC                                    |
|               Sort Method: quicksort  Memory: 3211kB                                                                                                 |
|               ->  Subquery Scan on guild_stats  (cost=21059.94..21622.51 rows=25003 width=70) (actual time=196.597..202.740 rows=25003 loops=1)      |
|                     ->  HashAggregate  (cost=21059.94..21372.48 rows=25003 width=70) (actual time=196.596..201.369 rows=25003 loops=1)               |
|                           Group Key: g.id                                                                                                            |
|                           Batches: 1  Memory Usage: 5905kB                                                                                           |
|                           ->  Hash Right Join  (cost=791.57..16559.88 rows=600008 width=42) (actual time=10.070..130.805 rows=479885 loops=1)        |
|                                 Hash Cond: (h.guild_id = g.id)                                                                                       |
|                                 ->  Seq Scan on hero h  (cost=0.00..14193.08 rows=600008 width=20) (actual time=0.028..32.655 rows=600008 loops=1)   |
|                                 ->  Hash  (cost=479.03..479.03 rows=25003 width=30) (actual time=9.927..9.927 rows=25003 loops=1)                    |
|                                       Buckets: 32768  Batches: 1  Memory Usage: 1831kB                                                               |
|                                       ->  Seq Scan on guild g  (cost=0.00..479.03 rows=25003 width=30) (actual time=0.013..4.224 rows=25003 loops=1) |
| Planning Time: 1.845 ms                                                                                                                              |
| Execution Time: 220.355 ms                                                                                                                           |

- **View Heroes**
  - **GET** `/world/view_heroes/{world_id}` - 149.76 ms

| QUERY PLAN                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------- |
| Bitmap Heap Scan on hero  (cost=1391.54..11116.07 rows=814 width=21) (actual time=9.574..99.470 rows=745 loops=1)                     |
|   Recheck Cond: (guild_id IS NULL)                                                                                                    |
|   Filter: (world_id = 1)                                                                                                              |
|   Rows Removed by Filter: 119381                                                                                                      |
|   Heap Blocks: exact=8193                                                                                                             |
|   ->  Bitmap Index Scan on hero_guild_id_idx  (cost=0.00..1391.34 rows=122522 width=0) (actual time=8.571..8.572 rows=120126 loops=1) |
|         Index Cond: (guild_id IS NULL)                                                                                                |
| Planning Time: 0.655 ms                                                                                                               |
| Execution Time: 99.637 ms                                                                                                             |

### Add Index
`CREATE INDEX ON hero (world_id);`

| QUERY PLAN                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------- |
| Bitmap Heap Scan on hero  (cost=1438.32..3836.03 rows=814 width=21) (actual time=9.101..45.591 rows=745 loops=1)                            |
|   Recheck Cond: ((world_id = 1) AND (guild_id IS NULL))                                                                                     |
|   Heap Blocks: exact=709                                                                                                                    |
|   ->  BitmapAnd  (cost=1438.32..1438.32 rows=814 width=0) (actual time=8.923..8.924 rows=0 loops=1)                                         |
|         ->  Bitmap Index Scan on hero_world_id_idx  (cost=0.00..46.32 rows=3986 width=0) (actual time=2.012..2.013 rows=4080 loops=1)       |
|               Index Cond: (world_id = 1)                                                                                                    |
|         ->  Bitmap Index Scan on hero_guild_id_idx  (cost=0.00..1391.34 rows=122522 width=0) (actual time=6.760..6.760 rows=120126 loops=1) |
|               Index Cond: (guild_id IS NULL)                                                                                                |
| Planning Time: 4.774 ms                                                                                                                     |
| Execution Time: 46.013 ms                                                                                                                   |


- **Find Monsters**
  - **GET** `/hero/find_monsters/{dungeon_id}` - 82.23 ms

| QUERY PLAN                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------- |
| Gather  (cost=1000.00..6121.53 rows=4 width=26) (actual time=4.066..44.524 rows=5 loops=1)                           |
|   Workers Planned: 1                                                                                                 |
|   Workers Launched: 1                                                                                                |
|   ->  Parallel Seq Scan on monster  (cost=0.00..5121.13 rows=2 width=26) (actual time=13.869..36.967 rows=2 loops=2) |
|         Filter: ((health > 0) AND (dungeon_id = 2))                                                                  |
|         Rows Removed by Filter: 150004                                                                               |
| Planning Time: 0.548 ms                                                                                              |
| Execution Time: 44.593 ms                                                                                            |
### Add Index
`CREATE INDEX ON monster(dungeon_id);`

| QUERY PLAN                                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------------------- |
| Bitmap Heap Scan on monster  (cost=4.45..20.03 rows=4 width=26) (actual time=0.298..0.601 rows=5 loops=1)                     |
|   Recheck Cond: (dungeon_id = 2)                                                                                              |
|   Filter: (health > 0)                                                                                                        |
|   Heap Blocks: exact=5                                                                                                        |
|   ->  Bitmap Index Scan on monster_dungeon_id_idx  (cost=0.00..4.45 rows=4 width=0) (actual time=0.278..0.278 rows=5 loops=1) |
|         Index Cond: (dungeon_id = 2)                                                                                          |
| Planning Time: 1.774 ms                                                                                                       |
| Execution Time: 0.734 ms                                                                                                      |
