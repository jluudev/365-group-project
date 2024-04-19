# Example Flows

## 1. Recruiting a Hero to Guild Example Flow
Mages Only wants to recruit a new hero into their guild because they need more power to clear the dungeons. First, they check the entire world of heroes by `GET /world/view_heroes/`. Mages Only sees that Elminster the Sage is not currently in a guild and that they had enough gold to recruit him. Mages Only wants to recruit Elminster the Sage because he's super powerful and having him would definitely increase their guild rank and gold. 

Mages Only then makes a request to Elminster the Sage.

To do so:
- Mages Only then sends a request to Elminster the Sage by calling `POST /guild/recruit_hero/{hero_id}/`
- Elminster the Sage calls `GET /hero/view_pending_requests/{hero_id}` one day because he is not in a guild. He sees the request from Mages Only.
- Elminster the Sage then has the option to accept by calling `POST /hero/accept_request/{guild_id}/`

Elminster the Sage accepts Mages Only and now he can join them in the dungeons.