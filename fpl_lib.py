import json
import asyncio
import aiohttp
from fpl import FPL
from fpl.models import * #classic_league import ClassicLeague
import logging
import random
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

LEAGUE_ID = 644545
# lazy, so just sleep id % 10 to avoid getting rate limited.
# also there's probably a way to do all this in one function and pass the user id and function to call.
async def map_id_to_picks(id, user):
    await asyncio.sleep(id % 10)
    return (id, await user.get_picks())

async def map_id_to_transfers(id, user):
    await asyncio.sleep(id % 10)
    return (id, await user.get_transfers())

async def wait_and_get_users(id, index, fpl1):
    logging.info(f"getting user data for id: {id}")
    await asyncio.sleep(index % 10)
    return await fpl1.get_user(id)

async def main():
    async with aiohttp.ClientSession() as session:
        fpl1 = FPL(session)
        await fpl1.login(email="shyam12860+fplmain@gmail.com", password="aragorn1")

        league = await fpl1.get_classic_league(LEAGUE_ID)

        tasks = [asyncio.create_task(wait_and_get_users(int(league.standings['results'][i]['entry']), i, fpl1)) for i in range(len(league.standings['results']))]

        print(len(tasks))
        result = await asyncio.gather(*tasks)

        logging.info(len(result))
        gw_tasks = [asyncio.create_task(map_id_to_transfers(u.id, u)) for u in result]
        gw_result = await asyncio.gather(*gw_tasks)
        gw_picks_map = {k:v for (k,v) in gw_result}
        with open("all_transfers.json", "w") as f:
            json.dump(gw_picks_map, f, indent = 4)
        users = [await fpl1.get_user(int(entry['entry'])) for entry in league.standings['results']]

async def common_data():
    async with aiohttp.ClientSession() as session:
        fpl1 = FPL(session)
        await fpl1.login(email="shyam12860+fplmain@gmail.com", password="aragorn1")

        all_gws = await fpl1.get_gameweeks(include_live=True, return_json=True)
        with open("gameweek.json", "w") as f:
            json.dump(all_gws, f, indent=4)

        all_players = await fpl1.get_players(include_summary=True, return_json=True)
        with open("player.json", "w") as f:
            json.dump(all_players, f, indent=4)

        fixtures = await fpl1.get_fixtures(return_json=True)
        with open("all_fixtures.json", "w") as f:
            json.dump(fixtures, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
