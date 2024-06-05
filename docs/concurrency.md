# Concurrency Control Mechanisms

### Case 1: Dirty Read

**Scenario**: The `/hero/check_health/{hero_id}/` endpoint reads the health of a hero that the `/monster/attack_hero/{monster_id}/` endpoint has updated but not yet committed. If the `/monster/attack_hero/{monster_id}/` transaction rolls back, the `/hero/check_health/{hero_id}/` endpoint will have read a value that never actually existed in the database.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant CheckHealth as /hero/check_health/{hero_id}/
    participant DB as Database
    participant AttackHero as /monster/attack_hero/{monster_id}/
    Note over CheckHealth, AttackHero: Initial state: hero health is 100
    AttackHero->>DB: UPDATE hero SET health = 50 WHERE id = 1
    CheckHealth->>DB: SELECT health FROM hero WHERE id = 1 (reads 50)
    AttackHero->>DB: ROLLBACK
    CheckHealth->>DB: Uses dirty value (health = 50)
    Note over CheckHealth, AttackHero: CheckHealth reads the incorrect health value.
```

### Case 2: Non-Repeatable Read

**Scenario**: The `/dungeon/assess_damage/{dungeon_id}/` endpoint reads the list of dead heroes in a dungeon. The `/guild/remove_dead_heroes/{guild_id}/` endpoint removes dead heroes from the guild and commits. When `/dungeon/assess_damage/{dungeon_id}/` reads the list again, it gets a different result.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant AssessDamage as /dungeon/assess_damage/{dungeon_id}/
    participant DB as Database
    participant RemoveHeroes as /guild/remove_dead_heroes/{guild_id}/
    Note over AssessDamage, RemoveHeroes: Initial state: 3 dead heroes in the dungeon
    AssessDamage->>DB: SELECT * FROM hero WHERE dungeon_id = 1 AND health <= 0 (returns 3 heroes)
    RemoveHeroes->>DB: DELETE FROM hero WHERE guild_id = 1 AND health <= 0
    RemoveHeroes->>DB: COMMIT
    AssessDamage->>DB: SELECT * FROM hero WHERE dungeon_id = 1 AND health <= 0 (returns 0 heroes)
    Note over AssessDamage, RemoveHeroes: AssessDamage sees different results for the same query.
```

### Case 3: Phantom Read

**Scenario**: The `/world/view_heroes/{world_id}` endpoint reads a list of heroes. The `/world/create_hero/{world_id} `endpoint inserts a new hero with power greater than 100 and commits. When `/world/view_heroes/{world_id}` reads the heroes again, it sees the new hero.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant ViewHeroes as /world/view_heroes/{world_id}
    participant DB as Database
    participant NewHero as /world/create_hero/{world_id}
    Note over ViewHeroes, NewHero: Initial state: 2 heroes in world
    ViewHeroes->>DB: SELECT * FROM hero WHERE guild_id = 1 AND power > 100 (returns 2 rows)
    NewHero->>DB: INSERT INTO hero (name, power, guild_id) VALUES ('NewHero', 150, NULL)
    NewHero->>DB: COMMIT
    ViewHeroes->>DB: SELECT * FROM hero WHERE guild_id = NULL (returns 3 rows)
    Note over ViewHeroes, NewHero: ViewHeroes sees the new hero inserted by NewHero.

```