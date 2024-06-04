-- Insert data into the world table
INSERT INTO world (name, dungeon_capacity, guild_capacity) VALUES 
    ('Scania', 50, 50),
    ('Bera', 100, 100),
    ('Windia', 50, 50),
    ('Galicia', 25, 25),
    ('Hyperion', 25, 25),
    ('Kronos', 100, 100),
    ('Nova', 50, 50),
    ('Zenith', 25, 25),
    ('El Nido', 25, 25),
    ('Demethos', 100, 100)
;

-- Insert data into the dungeon table
INSERT INTO dungeon (name, monster_capacity, party_capacity, level, gold_reward, world_id, status) VALUES
    ('Gold Beach', 10, 6, 5, 50, 1, 'closed'),
    ('Riena Strait', 10, 6, 5, 50, 2, 'open'),
    ('Monster Park', 10, 6, 5, 50, 3, 'open'),
    ('Secret Forest of Elodin', 10, 6, 5, 50, 4, 'open'),
    ('The Overgrown Ruins', 10, 6, 5, 50, 5, 'open'),
    ('Golem Temple', 10, 6, 5, 50, 6, 'open'),
    ('The Grave of a Wrecked Ship', 10, 6, 5, 50, 1, 'open'),
    ('Cernium', 10, 6, 5, 50, 1, 'closed')
;

-- Insert data into the monster table
INSERT INTO monster (type, level, health, power, dungeon_id) VALUES
    ('Coconut Slime', 4, 10, 3, 1),
    ('Coconut Slime', 5, 11, 4, 1),
    ('Coconut Slime', 4, 10, 3, 1),
    ('Coconut Slime', 5, 11, 4, 1),
    ('Coconut Slime', 4, 10, 3, 1),
    ('Coconut Slime', 4, 10, 3, 1),
    ('Coconut Slime', 5, 11, 4, 1),
    ('Coconut Slime', 4, 10, 3, 1),
    ('Zombie Mushroom', 9, 20, 5, 2),
    ('Jr. Balrog', 10, 50, 20, 3),
    ('Manon', 11, 60, 25, 4),
    ('Papulatus', 12, 70, 30, 5),
    ('Pianus', 13, 80, 35, 6),
    ('Bigfoot', 10, 50, 20, 2),
    ('Zakum', 12, 70, 30, 3),
    ('Horned Tail', 14, 90, 40, 4),
    ('Horntail', 14, 90, 40, 5),
    ('Balrog', 10, 50, 20, 2),
    ('Shade', 15, 100, 50, 6),
    ('Cyclops', 13, 80, 35, 1),
    ('Drake', 12, 70, 30, 2),
    ('Yeti', 11, 60, 25, 3)
;


-- Insert data into the guild table
INSERT INTO guild (name, player_capacity, gold, world_id) VALUES
    ('Mages Only', 25, 300, 1),
    ('NOOBZ', 50, 100, 2),
    ('Cool people only', 50, 100, 3),
    ('The Strongest', 50, 300, 4),
    ('PKers', 50, 100, 5),
    ('AFK', 10, 50, 6)
;

-- Insert data into the hero table
INSERT INTO hero (name, power, health, age, guild_id, world_id, level, xp) VALUES
    ('Wizard101', 10, 50, 68, 1, 1, 1, 0),
    ('Sorceress123', 10, 50, 100, 1, 1, 5, 0),
    ('OPbishop', 12, 25, 30, 2, 2, 3, 0),
    ('Bob', 5, 20, 5, NULL, 4, 2, 0),
    ('Joe', 10, 50, 34, NULL, 5, 9, 0),
    ('Bill', 10, 50, 20, NULL, 6, 7, 0),
    ('Dylan', 10, 50, 13, NULL, 1, 6, 0),
    ('Sara', 10, 50, 15, NULL, 2, 8, 0),
    ('Megan', 10, 50, 19, NULL, 3, 4, 0),
    ('Katie', 10, 50, 45, NULL, 4, 3, 0),
    ('Lily', 10, 50, 31, NULL, 5, 2, 0),
    ('Sophia', 10, 50, 96, NULL, 6, 1, 0),
    ('Olivia', 10, 50, 40, NULL, 1, 1, 0),
    ('Emily', 10, 50, 21, NULL, 2, 1, 0),
    ('Ava', 10, 50, 41, NULL, 3, 1, 0),
    ('Isabella', 10, 50, 52, NULL, 4, 1, 0),
    ('Mia', 10, 50, 34, NULL, 5, 1, 0),
    ('Abigail', 10, 50, 18, NULL, 6, 1, 0),
    ('Madison', 10, 50, 46, NULL, 1, 1, 0),
    ('Charlotte', 10, 50, 45, 1, 1, 10, 0)
;

-- Insert dead heroes that are still status = alive for testing
INSERT INTO hero (name, power, health, age, guild_id, dungeon_id, world_id, level, xp, status) VALUES
    ('Dead1', 10, 0, 100, 1, 1, 1, 1, 0, 'alive'),
    ('Dead2', 10, 0, 100, 1, 1, 1, 1, 0, 'alive'),
    ('Dead3', 10, 0, 100, 1, 1, 1, 1, 0, 'alive')
;

-- Insert hero party to a dungeon
INSERT INTO hero (name, power, health, age, guild_id, dungeon_id, world_id, level, xp) VALUES
    ('Harper', 10, 50, 43, 1, 1, 1, 10, 0),
    ('Scarlett', 10, 50, 64, 1, 1, 1, 10, 0),
    ('Aurora', 10, 50, 60, 1, 1, 1, 10, 0),
    ('Aria', 10, 50, 17, 1, 1, 1, 10, 0),
    ('Amelia', 10, 50, 55, 1, 1, 1, 10, 100)
;

-- Insert test data into targeting table
INSERT INTO targeting (hero_id, monster_id) VALUES
    (28, 1),
    (27, 2)
;
