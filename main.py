from app.database.insert import insert


def main():
    test_beatmap = (
        2667,  # MapID
        521,  # MapsetID
        "Ootsuki Kenji",  # Artist
        "Hitotoshite Jiku Ga Bureteiru",  # Title
        "Insane!!",  # Difficulty
        "14d001c1297e2f2fbe23b8463f437ff8",  # Md5
        0,  # Mode
        3.04,  # Stars
        "https://osu.ppy.sh/osu/2667",
    )

    insert(test_beatmap)


if __name__ == "__main__":
    main()
