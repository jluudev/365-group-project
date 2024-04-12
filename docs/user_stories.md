# User Stories

1. As a hero, I want to be able to leave the dungeon when I am low on health, so that I don't die.
2. As a monster, I want to be able to attack heroes, so that they die.
3. As a guild, I want to be able to recruit heroes, so that I can make more money.
4. As a dungeon, I want to be able to spawn monsters, so that it isn't empty.
5. As a hero I want to gain XP after killing a monster, so that I can spend XP to level up.
6. As a guild, I want to de-list dead heroes from my roster, so that I can keep a clean record.
7. As a hero, I want to receive gold after clearing a dungeon, so that I can make money.
8. As a hero, I want to share some of my gold to the guild, so that my guild is more powerful.
9. As a hero, I (don’t) want to age, so that I eventually die when I get too old.
10. As a dungeon, I want to have different average levels of monsters, so that there are different difficulties for each dungeon.
11. As a hero, I want to have different builds/classes, so that I can be unique from my allies.
12. As a hero, I want to have stamina, so that I can be tired after clearing some amount of dungeons.
13. As a guild, I want to group heroes up into parties, so together the heroes can clear tougher dungeons.
14. As a guild, I want to send heroes out on a quest, so that they can clear a dungeon and bring honor (and money) to the guild.
15. As a guild, I want to be ranked by money against other guilds, so that I can know who is the best guild.
16. As a hero, I want to be able to restore my stats like stamina, mana, or health with rest time, so that I can heal.
17. As a hero, I want to have a cool unique name, so I’m cool.
18. As a hero, I want to die after my health reaches 0, so that I am removed from the world.
19. As a hero, I want to spend money to go on vacation, so that I can relax and enjoy my life.

# Exceptions

1. Exception: Guild does not have money to recruit more heroes.
> - If a guild attempts to recruit a hero that costs more money than they have, then God says no.
2. Exception: Average level of a party of heroes is too low for a dungeon.
> - If a party of heroes attempt to clear a dungeon that is too high of a level for them, then the guild does not allow them to go to the dungeon.
3. Exception: Party of heroes is too large for a dungeon.
> - If a guild sends out a party of heroes that is too large in number for a dungeon, then they will not be able to fit inside the dungeon and will be stuck.
4. Exception: Hero tries to leave dungeon while in combat.
> - If a hero tries to leave the dungeon because he is low on health, but is in combat, the monster will stop them from escaping.
5. Exception: Hero that uses mana tries to fight a monster/dungeon without enough mana.
> - If a hero that uses mana tries to fight a monster without enough mana, they won’t be able to attack and will be prompted that they don’t have enough mana to use an attack.
6. Exception: Hero tries to go to a dungeon with not enough stamina.
> - If a hero tries to attempt a dungeon with low stamina, the guild will not allow them to.
7. Exception: A guild tries to send a party to a dungeon when there are 0 heroes in the guild.
> - If a guild has no heroes and attempts a dungeon, then an error occurs and since they don’t have anyone to clear the dungeon.
8. Exception: A guild tries to recruit a hero that has the same name as a current member.
> - If a guild attempts to recruit a hero when they have another hero of the same name, then the hero will refuse to join.
9. Exception: A hero tries to level up past 100.
> - If a hero tries to use XP to level up past 100, then an error occurs and the hero is told that they are at the max level.
10. Exception: Guild tries to send out a vacationing hero.
> - If a guild attempts to send a hero out on a quest, but the hero is on vacation, the hero sends an error and will say “go away.”
11. Exception: Dungeon attempts to spawn a monster, but the dungeon is at max capacity.
> - If a dungeon attempts to spawn a monster but the dungeon is in full capacity then then the monster won’t spawn and the dungeon remains unchanged.
12. Exception: Guild attempts to recruit a hero that is already a member of another guild.
> - If a guild tries to recruit a hero who is already part of another guild, the hero declines and remains with their current guild.
13. Exception: A party of heroes attempt to clear a dungeon when another party is already inside.
> - If a party of heroes attempt to go inside a dungeon that is already fighting inside, then the party that is fighting tells them to go away, and they are not allowed inside
