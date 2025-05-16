from tool.kialoTools import KialoSort, KialoFilter, getDiscussions, discussions2urlID
from tool.download import downloadDiscussions
from tool.sortFiles import classifyFilesByLanguage
import os

kialoUsername  = "PLACEHOLDER"
secret              = "PLACEHOLDER"

downloadPath = os.path.abspath("rawData/debates")

if __name__ == "__main__":
    downloadPathParent = os.path.abspath(os.path.join(downloadPath, os.pardir))

    # Export most active and high ranked kialo discussions
    getDiscussions(filter=KialoFilter.TAG, sort=KialoSort.RANK_ACTIVITY)
    debateIDs = discussions2urlID(getDiscussions(filter=KialoFilter.TAG, sort=KialoSort.RANK_ACTIVITY), export=True, exportPath=downloadPathParent)
    
    # Download the aforementioned discussions as text files
    print("Downloading discussions...")
    downloadDiscussions(debateIDs, kialoUsername, secret, downloadPath)
    print("Download complete.\n")

    # Sort the downloaded debates by language
    print("Sorting discussions by language...")
    classifyFilesByLanguage(downloadPath)

    # Print number of debates in each language
    languageFolders = [
        name 
        for name in os.listdir(downloadPath) 
        if os.path.isdir(os.path.join(downloadPath, name))
        ]

    for lang in languageFolders:
        lang_folder = os.path.join(downloadPath, lang)
        print(f"Language: {lang} -- Number of debates: {len(os.listdir(lang_folder))}")
