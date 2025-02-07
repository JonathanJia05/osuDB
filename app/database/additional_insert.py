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

limiter = AsyncLimiter(
    max_rate=370, time_period=60
)  # rate limiter since osu api has a max of 1200 requests/minute


async def authenticate(client: httpx.AsyncClient) -> str:
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
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{OSU_BASE_URL}/beatmaps/{map_id}"

    async with limiter:
        response = await client.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    play_count = data.get("playcount")
    if play_count is None:
        statistics = data.get("statistics", {})
        play_count = statistics.get("play_count", 0)

    max_combo = data.get("max_combo", 0)
    if not max_combo and "statistics" in data:
        statistics = data.get("statistics", {})
        max_combo = statistics.get("max_combo", 0)

    beatmapset = data.get("beatmapset", {})
    mapper = beatmapset.get("creator", "")

    covers = beatmapset.get("covers", {})
    imgurl = covers.get("card", "")

    return map_id, play_count, max_combo, mapper, imgurl


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

        batch_size = 370
        total_batches = (len(tasks) + batch_size - 1) // batch_size

        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            update_data = []
            for result in batch_results:
                if isinstance(result, Exception):
                    print("Error fetching details for a map:", type(result), result)
                else:
                    update_data.append((result[1], result[2], result[3], result[0]))
            print(f"Processed batch {(i // batch_size) + 1} of {total_batches}")

            try:
                with psycopg2.connect(**config) as conn:
                    with conn.cursor() as cur:
                        update_sql = """
                            UPDATE beatmaps
                            SET playcount = %s,
                                max_combo = %s,
                                mapper = %s
                            WHERE mapid = %s;
                        """
                        execute_batch(cur, update_sql, update_data, page_size=100)
                    conn.commit()
                print(
                    f"Updated extra fields for {len(update_data)} beatmaps in batch {(i // batch_size) + 1}"
                )
            except Exception as e:
                print(
                    "Error updating database for batch", (i // batch_size) + 1, ":", e
                )


if __name__ == "__main__":
    asyncio.run(update_all_maps())
