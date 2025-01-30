import psycopg2
from config import load_config


def create_tables():
    commands = [
        """
        CREATE TABLE beatmaps (
            MapID INTEGER PRIMARY KEY,
            MapsetID INTEGER NOT NULL,
            Artist TEXT,
            Title TEXT,
            Difficulty TEXT,
            Md5 TEXT UNIQUE,
            Mode INTEGER,
            Stars REAL
        )
        """
    ]
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as curr:
                for command in commands:
                    curr.execute(command)
            conn.commit()
            print("Tables successfully created")
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == "__main__":
    create_tables()
