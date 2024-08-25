import requests
import csv


url = "https://lichess.org/study/WW5CwKN5/bvOnLiUy"
name = "skewers"
headers = {
    "accept": "application/web.lichess+json",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Parse the JSON data as needed
    study_name = data["study"]["name"]
    fens = []
    for chapter in data["study"]["chapters"]:
        if "fen" in chapter:
            fens.append(chapter["fen"])

    csv_filename = f"lichess_study_fens_{name}.csv"
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["FEN"])
        for fens in fens:
            writer.writerow([fens])


else:
    print("Request failed with status code:", response.status_code)
