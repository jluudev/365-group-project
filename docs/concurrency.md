# Concurrency Control Mechanisms

### Case 1: Dirty Read

**Scenario**: Transaction A reads the health of a hero that Transaction B has updated but not committed. Transaction B then rolls back, but Transaction A has already read the uncommitted value.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant T1 as Transaction A
    participant DB as Database
    participant T2 as Transaction B
    Note over T1, T2: Initial state: hero health is 100
    T2->>DB: UPDATE hero SET health = 50 WHERE id = 1
    T1->>DB: SELECT health FROM hero WHERE id = 1 (reads 50)
    T2->>DB: ROLLBACK
    T1->>DB: Uses dirty value (health = 50)
    Note over T1, T2: T1 reads the incorrect health value.
```

### Case 2: Non-Repeatable Read

**Scenario**: Transaction A reads the gold of a guild. Transaction B updates the guild's gold and commits. Transaction A then reads the guild's gold again and gets a different result.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant T1 as Transaction A
    participant DB as Database
    participant T2 as Transaction B
    Note over T1, T2: Initial state: guild gold is 1000
    T1->>DB: SELECT gold FROM guild WHERE id = 1 (reads 1000)
    T2->>DB: UPDATE guild SET gold = 1500 WHERE id = 1
    T2->>DB: COMMIT
    T1->>DB: SELECT gold FROM guild WHERE id = 1 (reads 1500)
    Note over T1, T2: T1 sees different values for the same read.
```

### Case 3: Phantom Read

**Scenario**: Transaction A reads all heroes in a guild with power greater than 100. Transaction B inserts a new hero with power greater than 100 and commits. Transaction A then reads the heroes again and sees the new hero.

**Sequence Diagram**:

```mermaid
sequenceDiagram
    participant T1 as Transaction A
    participant DB as Database
    participant T2 as Transaction B
    Note over T1, T2: Initial state: 2 heroes in guild with power > 100
    T1->>DB: SELECT * FROM hero WHERE guild_id = 1 AND power > 100 (returns 2 rows)
    T2->>DB: INSERT INTO hero (name, power, guild_id) VALUES ('NewHero', 150, 1)
    T2->>DB: COMMIT
    T1->>DB: SELECT * FROM hero WHERE guild_id = 1 AND power > 100 (returns 3 rows)
    Note over T1, T2: T1 sees the new hero inserted by T2.
```