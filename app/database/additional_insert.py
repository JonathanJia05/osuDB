import os
import asyncio
import httpx
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
from aiolimiter import AsyncLimiter
from .config import load_config

load_dotenv(override=True)

OSU_BASE_URL = "https://osu.ppy.sh/api/v2"
OSU_AUTH_URL = "https://osu.ppy.sh/oauth/token"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

limiter = AsyncLimiter(max_rate=370, time_period=60)


async def authenticate(client: httpx.AsyncClient) -> str:
    """
    Authenticate with the osu! API and return an access token.
    """
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "public",
    }
    response = await client.post(OSU_AUTH_URL, json=payload)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("Authenticated with osu! API")
    return token


async def fetch_map_details(map_id: int, client: httpx.AsyncClient, access_token: str):
    """
    Fetch details for a beatmap using its map_id.
    Returns a tuple: (map_id, play_count, max_combo, imgurl)
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{OSU_BASE_URL}/beatmaps/{map_id}"

    async with limiter:
        response = await client.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    statistics = data.get("statistics", {})
    play_count = statistics.get("play_count", 0)

    max_combo = data.get("max_combo", 0)
    if not max_combo and "max_combo" in statistics:
        max_combo = statistics["max_combo"]

    beatmapset = data.get("beatmapset", {})
    covers = beatmapset.get("covers", {})
    imgurl = covers.get("card", "")

    return map_id, play_count, max_combo, imgurl


async def update_all_maps():
    config = load_config()

    map_ids = []
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT mapid FROM beatmaps;")
                rows = cur.fetchall()
                map_ids = [row[0] for row in rows]
        print(f"Found {len(map_ids)} beatmaps to update")
    except Exception as e:
        print("Error fetching map IDs:", e)
        return

    async with httpx.AsyncClient() as client:
        access_token = await authenticate(client)

        tasks = [fetch_map_details(map_id, client, access_token) for map_id in map_ids]

        results = []
        batch_size = 370
        total_batches = (len(tasks) + batch_size - 1) // batch_size
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            for result in batch_results:
                if isinstance(result, Exception):
                    print("Error fetching details for a map:", result)
                else:
                    results.append(result)
            print(f"Processed batch {(i // batch_size) + 1} of {total_batches}")

    update_data = [
        (play_count, max_combo, map_id) for map_id, play_count, max_combo, _ in results
    ]

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                update_sql = """
                    UPDATE beatmaps
                    SET playcount = %s,
                        max_combo = %s
                    WHERE mapid = %s;
                """
                execute_batch(cur, update_sql, update_data, page_size=100)
            conn.commit()
        print(f"Updated extra fields for {len(update_data)} beatmaps")
    except Exception as e:
        print("Error updating database:", e)


if __name__ == "__main__":
    asyncio.run(update_all_maps())
