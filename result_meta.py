import re
from datetime import datetime, timedelta
from utils import *

def add_result_meta(rows, results, result_file):
    def _get_short_name(division):
        m = re.search("[0-9]", division)
        if m != None:
            nb = m.group(0)
        m = re.search("Junior|Senior", division)
        if m != None:
            div = m.group(0)
        m = re.search("South|North|West", division)
        if m != None:
            zone = m.group(0)
        try:
            return f"{div}-{nb}-{zone}"
        except:
            return f"{div}-{nb}"

    def _get_all_matches(team_name, results, type="Home"):
        def conv_date(str):
            d = datetime.strptime(str, "%Y/%m/%d")
            return d

        matches = []
        for a_result in results:
            if type == "Home" and a_result["Home"] == team_name:
                matches.append(a_result)
            if type == "Away" and a_result["Away"] == team_name:
                matches.append(a_result)
        matches = sorted(matches, key=lambda d: conv_date(d["Date"]))
        return matches

    def _get_gap(home_team, away_team, matches):
        matched = []
        for match in matches:
            if (match["Home"] == home_team and match["Away"] == away_team) or (
                match["Away"] == home_team and match["Home"] == away_team
            ):
                matched.append(match)
        assert 2 == len(matched)
        match_date = datetime.strptime(matched[0]["Date"], "%Y/%m/%d")
        prev_match_date = datetime.strptime(matched[1]["Date"], "%Y/%m/%d")
        difference = abs((match_date - prev_match_date).days)
        return difference / 7

    def _get_max_consecutive(team, results, type="Home"):
        # matches are ordered by date
        matches = _get_all_matches(team, results, type)
        max_consecutive = 0
        prev_match = None
        consecutive = 1
        for match in matches:
            if prev_match == None:
                consecutive = 1
            else:
                match_date = datetime.strptime(match["Date"], "%Y/%m/%d")
                prev_match_date = datetime.strptime(prev_match["Date"], "%Y/%m/%d")
                assert match_date > prev_match_date
                difference = (match_date - prev_match_date).days
                if difference == 7:
                    consecutive += 1
                else:
                    consecutive = 1
            if consecutive > max_consecutive:
                max_consecutive = consecutive
            prev_match = match
        return max_consecutive

    div_dict = {}
    for division in get_all_divisions(rows):
        result_metas = []
        for home_team in get_all_teams(rows, division):
            # row = get_row_for_team(rows, home_team)
            meta = {}
            meta["home_team"] = home_team
            meta["home_cons"] = _get_max_consecutive(home_team, results, "Home")
            meta["away_cons"] = _get_max_consecutive(home_team, results, "Away")
            for away_team in get_all_teams(rows, division):
                if home_team == away_team:
                    meta[home_team] = "-"
                    continue
                meta[away_team] = _get_gap(home_team, away_team, results)
            result_metas.append(meta)
        sorted_metas = []

        div = _get_short_name(division)
        for meta in result_metas:
            sorted_metas.append(dict(sorted(meta.items())))
        div_dict[div] = sorted_metas
    update_excel(result_file, sheets_dict=div_dict)
