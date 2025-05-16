from enum import Enum
import requests
import pandas as pd
import os

class KialoSort(Enum):
  RANK_ACTIVITY = "rank_and_latest_activity"
  VIEW          = "view_count"
  LAST_ACTIVITY = "latest_activity"

class KialoFilter(Enum):
  PROMOTED      = "promoted"
  PARTICIPATE   = "participate"
  LAST_ACTIVITY = "latest_activity"
  TAG           = "tag"
  TAG_ALL       = "tag_all"

def getDiscussions(filter: KialoFilter, sort: KialoSort, limit : int=3000) -> list[dict]:
    """Send API request to get discussions from Kialo based on filter and sort options.

    Args:
        filter (KialoFilter): Filter option for discussions
        sort (KialoSort): Sorting option for discussions
        limit (int, optional): Maximum number of discussions to request. Defaults to 3000.

    Returns:
        list[dict]: List of discussion objects containing title, id, and tags
    """
    req = "https://www.kialo.com/api/v1/discussions?filter=" + str(filter.value) + "&sort=" + str(sort.value) + "&limit=" + str(limit) + "&skip=0"
    tags = requests.get(req)
    return tags.json()["discussions"]

def replaceSpecialChars(string : str) -> str:
    """Replace special characters found in discussion titles with URL-friendly characters.

    Args:
        string (str): Discussion title

    Returns:
        str: Sanitized URL string ready for request 
    """
    string = string.replace("?", "").replace(" ", "-")
    string = string.replace("/", "").replace("(", "").replace(")","")
    string = string.replace(":", "").replace(",", "").replace(".", "").replace(";", "")
    string = string.replace("'", "").replace('"', "") # remove quotes and apostrophes
    string = string.replace("%", "").replace("#", "")
    return string

def discussions2urlID(discussions : list[dict], export : bool =False, exportPath : os.path = os.path.abspath("../rawData")) -> list[str]:
    """Convert discussion titles to URL-friendly IDs by removing special characters and appending the discussion ID. Can save the resulting list to a CSV file named "kialo-url-ids.csv".

    Args:
        discussions (list[dict]): List of discussion objects containing title and id
        export (bool, optional): Whether to save or not the resulting list to CSV format. Defaults to False.
        exportPath (os.path, optional): Path of folder to save the CSV file into. Defaults to "../rawData".

    Returns:
        list[str]: List of URL IDs to use for downloading discussions
    """
    idsUrl = [replaceSpecialChars(x["title"].lower())+"-"+str(x["id"]) for x in discussions]
    tags = [x["tags"] for x in discussions]
    if export:
        if not os.path.exists(exportPath):
            os.makedirs(exportPath)
        pd.DataFrame.from_dict({"kialoUrlId" : idsUrl, "tags" : tags}).to_csv(os.path.join(exportPath, "kialo-url-ids.csv"))

    return idsUrl