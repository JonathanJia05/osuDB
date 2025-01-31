from app.database.insert import insert


# testing function
def main():
    test_beatmap = (
        2667,
        521,
        "Ootsuki Kenji",
        "Hitotoshite Jiku Ga Bureteiru",
        "Insane!!",
        "14d001c1297e2f2fbe23b8463f437ff8",
        0,
        3.04,
        "https://osu.ppy.sh/osu/2667",
    )

    insert(test_beatmap)


if __name__ == "__main__":
    main()
