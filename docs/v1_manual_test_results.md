# Example workflow

## 1. Recruiting a Hero to Guild Example Flow
Mages Only wants to recruit a new hero into their guild because they need more power to clear the dungeons. First, they check the entire world of heroes by `GET /world/view_heroes/{world_id}`. Mages Only sees that Elminster the Sage is not currently in a guild and that they had enough gold to recruit him. Mages Only wants to recruit Elminster the Sage because he's super powerful and having him would definitely increase their guild rank and gold. 

Mages Only then makes a request to Elminster the Sage.

To do so:
- Mages Only then sends a request to Elminster the Sage by calling `POST /guild/recruit_hero/{guild_id}/` with Elminster the Sage as the hero name.
- Elminster the Sage calls `GET /hero/view_pending_requests/{hero_id}` one day because he is not in a guild. He sees the request from Mages Only.
- Elminster the Sage then has the option to accept by calling `POST /hero/accept_request/{hero_id}/` with the Mages Only as the request input

Elminster the Sage accepts Mages Only and now he can join them in the dungeons.

# Testing results
1. `GET /world/view_heroes/{world_id}`

    #### Find all heroes not in a guild in Scania (world_id = 1)
    ```
    curl -X 'GET' \
    'http://arthurslastcrusade.onrender.com/world/view_heroes/1' \
    -H 'accept: application/json' \
    -H 'access_token: test'
    ```

    Response body:
    ```json
        "heroes": [
            {
            "name": "Dylan",
            "power": 10,
            "health": 50
            }
        ]
    ```

2. `POST /guild/recruit_hero/{guild_id}/`
    
    #### Mages Only (guild_id = 1) want to recruit hero (Dylan) that is not in a guild.
    ```
    curl -X 'POST' \
    'http://arthurslastcrusade.onrender.com/guild/recruit_hero/1' \
    -H 'accept: application/json' \
    -H 'access_token: test' \
    -H 'Content-Type: application/json' \
    -d '{
    "hero_name": "Dylan"
    }'
    ```
    Response body:
    ```json
        {
            "success": true
        }
    ```

    #### Mages Only (guild_id = 1) want to recruit hero (Bob) that is already in a guild.

    ```
    curl -X 'POST' \
    'http://arthurslastcrusade.onrender.com/guild/recruit_hero/1' \
    -H 'accept: application/json' \
    -H 'access_token: test' \
    -H 'Content-Type: application/json' \
    -d '{
    "hero_name": "Dylan"
    }'
    ```
    Response body:
    ```json
        {
            "success": false,
            "message": "Hero not found or already in a guild"
        }
    ```

3. `GET /hero/view_pending_requests/{hero_id}`
    #### Dylan (hero_id = 7) checks all their pending guild requests

    ```
    curl -X 'GET' \
    'http://arthurslastcrusade.onrender.com/hero/view_pending_requests/7' \
    -H 'accept: application/json' \
    -H 'access_token: test'
    ```

    Response body:
    ```json
        [
            {
                "guild_name": "Mages Only",
                "gold": 300
            }
        ]
    ```

4. `POST /hero/accept_request/{hero_id}/`
    #### Dylan (hero_id = 7) accepts pending request from Mages Only

    ```
    curl -X 'POST' \
    'http://arthurslastcrusade.onrender.com/hero/accept_request/7?guild_name=Mages%20Only' \
    -H 'accept: application/json' \
    -H 'access_token: test' \
    -d ''
    ```

    Response body:
    ```json
        {
            "success": true
        }
    ```
