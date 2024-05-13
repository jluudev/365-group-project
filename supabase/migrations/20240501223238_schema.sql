-- Table for World
CREATE TABLE world (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    dungeon_capacity INT,
    guild_capacity INT
);

-- Table for Dungeon
CREATE TABLE dungeon (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    monster_capacity INT,
    party_capacity INT,
    level INT,
    gold_reward INT,
    world_id BIGINT REFERENCES world(id),
    status TEXT DEFAULT 'open' -- Examples: 'open', 'closed'
);

-- Table for Monster
CREATE TABLE monster (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    type TEXT NOT NULL,
    level INT,
    health INT,
    power INT,
    dungeon_id BIGINT REFERENCES dungeon(id)
);

-- Table for Guild
CREATE TABLE guild (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    player_capacity INT,
    gold INT,
    world_id BIGINT REFERENCES world(id)
);

-- Table for Hero
CREATE TABLE hero (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    power INT,
    health INT,
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    status TEXT DEFAULT 'alive', -- Examples: 'alive', 'dead'
    guild_id BIGINT REFERENCES guild(id),
    dungeon_id BIGINT REFERENCES dungeon(id),
    world_id BIGINT REFERENCES world(id)
);

-- Table for Recruitment
CREATE TABLE recruitment (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    hero_id BIGINT REFERENCES hero(id),
    guild_id BIGINT REFERENCES guild(id),
    status TEXT NOT NULL, -- Examples: 'pending', 'accepted', 'rejected'
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    response_date TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Table for Monster/Hero targeting
CREATE TABLE targeting (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    hero_id BIGINT REFERENCES hero(id),
    monster_id BIGINT REFERENCES monster(id)
);

-- Create View for Damage Assessment
CREATE VIEW damage_assessment AS
SELECT dungeon_id, id AS hero_id
FROM hero
WHERE health = 0;