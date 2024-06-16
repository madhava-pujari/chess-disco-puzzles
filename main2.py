import requests
import csv


url = "https://lichess.org/study/r1sPtVdy/rVoFJZxl"

headers = {
    "accept": "application/web.lichess+json",
    "referer": "https://lichess.org/study/wpCNEljM/gZ0s0Bml",
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

    # Write the FEN strings to a CSV file
    csv_filename = "lichess_study_fens.csv"
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow([study_name])
        # Write each FEN string in a new row
        for fens in fens:
            writer.writerow([fens])


else:
    print("Request failed with status code:", response.status_code)
