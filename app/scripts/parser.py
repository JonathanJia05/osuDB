import os
import json
from pathlib import Path
from app.database.insert import insert

DATA_FOLDER = Path(__file__).parent.parent.parent / "data"


def loadJSON():
    total_maps = 0
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            file_path = DATA_FOLDER / filename
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    json_data = json.load(file)
                    beatmaps = []

                    for entry in json_data:
                        for beatmap in entry.get("Beatmaps", []):
                            beatmaps.append(
                                (
                                    beatmap["MapId"],
                                    beatmap["MapSetId"],
                                    beatmap["ArtistRoman"],
                                    beatmap["TitleRoman"],
                                    beatmap["DiffName"],
                                    beatmap["Md5"],
                                    beatmap["PlayMode"],
                                    beatmap["StarsNomod"],
                                    f"https://osu.ppy.sh/osu/{beatmap['MapId']}",
                                )
                            )

                    if beatmaps:
                        insert(beatmaps)
                        total_maps += len(beatmaps)
                        print(f"Inserted {len(beatmaps)} maps from {filename}")

                except (json.JSONDecodeError, KeyError) as error:
                    print(f"Error loading {filename}: {error}")

    print(f"{total_maps} total maps inserted")


if __name__ == "__main__":
    loadJSON()
