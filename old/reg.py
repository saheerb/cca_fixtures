from datetime import datetime, timedelta

from operator import itemgetter

def _get_max_consecutive():
    def conv_date(str):
       d = datetime.strptime(str, "%Y/%m/%d")
       return d

    matches=[{'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Upwood CC - 2nd XI', 'Away Team ID': '11685', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/06/15', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'City of Ely CC - 2nd XI', 'Away Team ID': '50532', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/05/11', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Kimbolton CC - 2nd XI', 'Away Team ID': '207084', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/07/06', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Cam Kerala CC - 1st XI', 'Away Team ID': '145322', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/06/29', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Sutton CC, Cambs - 1st XI', 'Away Team ID': '63723', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/06/01', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Bottisham and Lode CC - 1st XI', 'Away Team ID': '60932', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/08/24', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Burwell and Exning CC - 2nd XI', 'Away Team ID': '224865', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/05/04', 'Time': '13:00'}, {'Division': 'CCA Junior League 1 North', 'Division ID': '117770', 'Home': 'Needingworth CC - 1st XI', 'Home Team ID': '60631', 'Away': 'Girton CC - 1st XI', 'Away Team ID': '42059', 'Ground': 'Millfields', 'Ground ID': '4570', 'Date': '2024/08/03', 'Time': '13:00'}]

    # matches are ordered by date
    max_consecutive = 0
    prev_match = None
    consecutive = 1
    newlist = sorted(matches, key=lambda d: conv_date(d['Date']))
    # newlist = sorted(matches, key=itemgetter('Date')) 
    for match in newlist:
      print (match["Date"])
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

_get_max_consecutive()