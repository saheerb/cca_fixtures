import requests
import re
from bs4 import BeautifulSoup
import pylightxl as xl
import json
from pathlib import Path


def get_data_from_play_cricket():
    pattern = re.compile(r"website/division/*")

    BASE_URL = "https://cambhuntpremierleague.play-cricket.com/"
    main_page = requests.get(BASE_URL)

    main_soup = BeautifulSoup(main_page.content, "html.parser")
    div_links = main_soup.find_all("a", href=re.compile(r"website/division/*"))
    data = []
    for div_link in div_links:
        div_url = div_link.get("href")
        div_name = div_link.text
        div_page = requests.get(BASE_URL + div_url)
        div_soup = BeautifulSoup(div_page.content, "html.parser")
        team_links = div_soup.find_all("a", href=re.compile(r"Teams/*"))
        for team_link in team_links:
            team_url = team_link.get("href")
            team_name = team_link.text
            team_page = requests.get(team_url)

            team_soup = BeautifulSoup(team_page.content, "html.parser")
            mydiv = team_soup.find("div", {"class": "titleinfo-team-right"})
            p_list = mydiv.find("div")
            team = p_list.find("h3")
            ground_link = team_soup.find("a", href=re.compile(r"grounds/*"))
            if ground_link == None:
                print(f"No ground for {team_link.text}")
                ground_name = ""
                ground_url = ""
            else:
                ground_name = ground_link.text.strip()
                ground_url = ground_link.get("href")

            this = {
                "div_url": div_url,
                "div_name": div_name,
                "team_url": team_url,
                "club_name": team_name,
                "team_name": team.text,
                "ground_url": ground_url,
                "ground_name": ground_name,
            }
            data.append(this)
    return data


if __name__ == "__main__":
    working_dir = "2024/tmp"
    result_file = "data.json"
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    data = get_data_from_play_cricket()
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
