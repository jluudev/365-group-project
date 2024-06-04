import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the base URL and access token from the environment variables
base_url = os.getenv("BASE_URL")
access_token = os.getenv("ACCESS_TOKEN")

headers = {
    "accept": "application/json",
    "access_token": access_token
}

# Function to hit an endpoint and measure execution time
def hit_endpoint(method, url, params=None, data=None):
    full_url = f"{base_url}{url}"
    start_time = time.time()
    
    if method == "GET":
        response = requests.get(full_url, params=params, headers=headers)
    elif method == "POST":
        response = requests.post(full_url, params=params, json=data, headers=headers)
    
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    if response.status_code != 200:
        print(f"Error hitting {full_url}: {response.status_code} - {response.text}")
    
    return execution_time, response

def get_json_response(response):
    try:
        return response.json()
    except ValueError:
        print(f"Error: Expected JSON response but got: {response.text}")
        return None

# Example Flow 1: Recruiting a Hero to Guild
def recruit_hero_to_guild(execution_times):
    # Step 1: View heroes in a world
    exec_time, response = hit_endpoint("GET", "/world/view_heroes/1")
    print(f"View Heroes: {exec_time:.2f} ms")
    execution_times.append(("/world/view_heroes/1", exec_time))
    heroes = get_json_response(response)
    if not heroes:
        return

    print(f"Heroes response: {heroes}")

    target_hero = None

    for hero in heroes:
        if isinstance(hero, dict) and hero.get('guild_id') is None:
            target_hero = hero
            break

    if not target_hero:
        print("No available hero found for recruitment.")
        return

    hero_name = target_hero.get('name')
    hero_id = target_hero.get('id')
    print(f"Target Hero: {hero_name}, ID: {hero_id}")

    if not hero_id:
        print("Error: Target hero does not have an ID.")
        return

    # Step 2: Recruit the hero
    exec_time, response = hit_endpoint("POST", "/guild/recruit_hero/1", data={"hero_name": hero_name})
    print(f"Recruit Hero: {exec_time:.2f} ms")
    execution_times.append(("/guild/recruit_hero/1", exec_time))

    # Step 3: Hero views pending requests
    exec_time, response = hit_endpoint("GET", f"/hero/view_pending_requests/{hero_id}")
    print(f"View Pending Requests: {exec_time:.2f} ms")
    execution_times.append((f"/hero/view_pending_requests/{hero_id}", exec_time))

    # Step 4: Hero accepts the request
    exec_time, response = hit_endpoint("POST", f"/hero/accept_request/{hero_id}", params={"guild_name": "Mages Only"})
    print(f"Accept Request: {exec_time:.2f} ms")
    execution_times.append((f"/hero/accept_request/{hero_id}", exec_time))

# Example Flow 2: Sending a Party to a Dungeon and Collecting Bounty
def send_party_to_dungeon(execution_times):
    # Step 1: Get available dungeons (quests)
    exec_time, response = hit_endpoint("GET", "/world/get_quests/1")
    print(f"Get Quests: {exec_time:.2f} ms")
    execution_times.append(("/world/get_quests/1", exec_time))
    dungeons = get_json_response(response)
    if not dungeons:
        return

    target_dungeon = None

    for dungeon in dungeons:
        if isinstance(dungeon, dict) and dungeon.get('dungeon_level') == 27 and dungeon.get('player_capacity') >= 5:
            target_dungeon = dungeon
            break

    if not target_dungeon:
        print("No suitable dungeon found.")
        return

    dungeon_name = target_dungeon.get('dungeon_name')
    dungeon_id = target_dungeon.get('id')
    print(f"Target Dungeon: {dungeon_name}, ID: {dungeon_id}")

    if not dungeon_id:
        print("Error: Target dungeon does not have an ID.")
        return

    # Step 2: Get available heroes in the guild
    exec_time, response = hit_endpoint("GET", "/guild/available_heroes/1")
    print(f"Available Heroes: {exec_time:.2f} ms")
    execution_times.append(("/guild/available_heroes/1", exec_time))
    heroes = get_json_response(response)
    if not heroes:
        return

    party = heroes[:5]  # Select 5 heroes for the party

    # Step 3: Send party to the dungeon
    hero_names = [hero.get('hero_name') for hero in party]
    exec_time, response = hit_endpoint("POST", "/guild/send_party/1", params={"dungeon_name": dungeon_name}, data={"party": hero_names})
    print(f"Send Party: {exec_time:.2f} ms")
    execution_times.append(("/guild/send_party/1", exec_time))

    # Step 4: Collect bounty after dungeon is cleared
    exec_time, response = hit_endpoint("POST", "/dungeon/collect_bounty/1", params={"dungeon_id": dungeon_id})
    print(f"Collect Bounty: {exec_time:.2f} ms")
    execution_times.append(("/dungeon/collect_bounty/1", exec_time))

    # Step 5: Assess damage after dungeon is cleared
    exec_time, response = hit_endpoint("GET", f"/dungeon/assess_damage/{dungeon_id}", params={"guild_id": 1})
    print(f"Assess Damage: {exec_time:.2f} ms")
    execution_times.append((f"/dungeon/assess_damage/{dungeon_id}", exec_time))
    damages = get_json_response(response)
    if not damages:
        return

    # Remove dead heroes
    dead_heroes = [hero for hero in damages if hero.get('health') <= 0]
    if dead_heroes:
        dead_hero_names = [hero.get('hero_name') for hero in dead_heroes]
        exec_time, response = hit_endpoint("POST", "/guild/remove_heroes/1", data={"heroes": dead_hero_names})
        print(f"Remove Heroes: {exec_time:.2f} ms")
        execution_times.append(("/guild/remove_heroes/1", exec_time))

# Example Flow 3: Party Fights and Clears a Dungeon
def party_fights_and_clears_dungeon(execution_times):
    # Step 1: Find monsters in a dungeon
    exec_time, response = hit_endpoint("GET", "/hero/find_monsters/1")
    print(f"Find Monsters: {exec_time:.2f} ms")
    execution_times.append(("/hero/find_monsters/1", exec_time))
    monsters = get_json_response(response)
    if not monsters:
        return

    print(f"Monsters response: {monsters}")

    # Simulate fights between heroes and monsters
    for monster in monsters:
        if isinstance(monster, dict):
            monster_id = monster.get('id')
            exec_time, response = hit_endpoint("POST", f"/hero/attack_monster/1", params={"monster_id": monster_id})
            print(f"Attack Monster: {exec_time:.2f} ms")
            execution_times.append((f"/hero/attack_monster/1", exec_time))

            # Monster attacks hero back
            exec_time, response = hit_endpoint("POST", f"/monster/attack_hero/{monster_id}", params={"hero_id": 1})
            print(f"Attack Hero: {exec_time:.2f} ms")
            execution_times.append((f"/monster/attack_hero/{monster_id}", exec_time))

            # Check if monster is dead
            monster_response = get_json_response(response)
            if monster_response and monster_response.get('health') is not None and monster_response['health'] <= 0:
                exec_time, response = hit_endpoint("POST", f"/monster/die/{monster_id}")
                print(f"Monster Die: {exec_time:.2f} ms")
                execution_times.append((f"/monster/die/{monster_id}", exec_time))
            else:
                # Hero might run away
                exec_time, response = hit_endpoint("POST", f"/hero/run_away/1")
                print(f"Run Away: {exec_time:.2f} ms")
                execution_times.append((f"/hero/run_away/1", exec_time))

    # After the battle, heroes check their XP and level up if possible
    exec_time, response = hit_endpoint("GET", f"/hero/check_xp/1")
    print(f"Check XP: {exec_time:.2f} ms")
    execution_times.append((f"/hero/check_xp/1", exec_time))

    hero_response = get_json_response(response)
    if hero_response and hero_response.get('xp') is not None and hero_response['xp'] >= 100:  # Example condition to raise level
        exec_time, response = hit_endpoint("POST", f"/hero/raise_level/1")
        print(f"Raise Level: {exec_time:.2f} ms")
        execution_times.append((f"/hero/raise_level/1", exec_time))

# Remaining Endpoints Testing
def test_remaining_endpoints(execution_times):
    endpoints = [
        {"method": "POST", "url": "/world/create_hero/1", "data": {"hero_name": "TestHero7", "classType": "Warrior", "level": 1, "age": 20, "power": 100, "health": 100}},
        {"method": "POST", "url": "/world/age_hero/1"},
        {"method": "POST", "url": "/dungeon/create_dungeon/1", "data": {"dungeon_name": "TestDungeon7", "dungeon_level": 1, "player_capacity": 5, "monster_capacity": 10, "reward": 100}},
        {"method": "POST", "url": "/dungeon/create_monster/1", "data": {"type": "Dragon", "health": 500, "power": 300, "level": 10}},
        {"method": "GET", "url": "/hero/check_health/1"},
        {"method": "POST", "url": "/hero/die/1"},
        {"method": "GET", "url": "/hero/1/monster_interactions"},
        {"method": "GET", "url": "/monster/find_heroes/1"},
        {"method": "POST", "url": "/guild/create_guild/1", "data": {"guild_name": "TestGuild", "max_capacity": 50, "gold": 1000}},
        {"method": "GET", "url": "/guild/leaderboard"},
    ]

    for endpoint in endpoints:
        exec_time, response = hit_endpoint(endpoint["method"], endpoint["url"], endpoint.get("params"), endpoint.get("data"))
        execution_times.append((endpoint["url"], exec_time))
        print(f"Endpoint: {endpoint['url']} | Execution time: {exec_time:.2f} ms")

# Run example flows and test remaining endpoints
execution_times = []
recruit_hero_to_guild(execution_times)
send_party_to_dungeon(execution_times)
party_fights_and_clears_dungeon(execution_times)
test_remaining_endpoints(execution_times)

# Find the three slowest endpoints
slowest_endpoints = sorted(execution_times, key=lambda x: x[1], reverse=True)[:3]
print("\nThree slowest endpoints:")
for url, exec_time in slowest_endpoints:
    print(f"Endpoint: {url} | Execution time: {exec_time:.2f} ms")
