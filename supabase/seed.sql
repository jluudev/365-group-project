INSERT INTO world (name, dungeon_capacity, guild_capacity) VALUES 
  ('Scania', 50, 50),
  ('Bera', 100, 100),
  ('Windia', 50, 50),
  ('Galicia', 25, 25),
  ('Hyperion', 25, 25),
  ('Kronos', 100, 100)
;

INSERT INTO dungeon (name, monster_capacity, party_capacity, level, gold_reward, world_id) VALUES
  ('Gold Beach', 10, 6, 5, 50, 1),
  ('Riena Strait', 10, 6, 5, 50, 2),
  ('Monster Park', 10, 6, 5, 50, 3),
  ('Secret Forest of Elodin', 10, 6, 5, 50, 4),
  ('The Overgrown Ruins', 10, 6, 5, 50, 5),
  ('Golem Temple', 10, 6, 5, 50, 6 )
;

INSERT INTO monster (type, level, health, power, dungeon_id) VALUES
  ('Coconut Slime', 4, 10, 3, 1),
  ('Coconut Slime', 5, 11, 4, 1),
  ('Coconut Slime', 4, 10, 3, 1),
  ('Coconut Slime', 5, 11, 4, 1),
  ('Coconut Slime', 4, 10, 3, 1),
  ('Coconut Slime', 4, 10, 3, 1),
  ('Coconut Slime', 5, 11, 4, 1),
  ('Coconut Slime', 4, 10, 3, 1)
;

INSERT INTO guild (name, player_capacity, gold, world_id) VALUES
  ('Mages Only', 25, 300, 1),
  ('NOOBZ', 50, 100, 2),
  ('Cool people only', 50, 100, 3),
  ('The Strongest', 50, 300, 4),
  ('PKers', 50, 100, 5),
  ('AFK', 10, 50, 6)
;

INSERT INTO hero (name, power, health, guild_id, world_id, level, xp) VALUES
  ('Wizard101', 10, 50, 1, 1, 1, 0),
  ('Sorceress123', 10, 50, 1, 1, 5, 0),
  ('OPbishop', 12, 25, 2, 2, 3, 0),
  ('Bob', 5, 20, NULL, 4, 2, 0),
  ('Joe', 10, 50, NULL, 5, 9, 0),
  ('Bill', 10, 50, NULL, 6, 7, 0),
  ('Dylan', 10, 50, NULL, 1, 6, 0)
;