import psycopg2
from .config import load_config


def insert(beatmapData):
    sql = """
        INSERT INTO beatmaps(
            MapID, 
            MapsetID, 
            Artist, 
            Title, 
            Difficulty, 
            Md5, 
            Mode, 
            Stars,
            OsuURL
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (MapID) DO NOTHING;
    """

    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as curr:
                curr.executemany(sql, beatmapData)
            conn.commit()
        print(f"{len(beatmapData)} beatmaps inserted")
    except (psycopg2.DatabaseError, Exception) as error:
        print("Error inserting beatmap:", error)
    finally:
        conn.close()
