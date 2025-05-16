import os, shutil
from langdetect import detect, LangDetectException

def classifyFilesByLanguage(baseFolderPath : os.path):
    """Classify debate files by their language. Will sort them into folders named after the detected language. 
    The folders will be created in the same directory as the original files. 
    The original files will be copied to the new folders. 
    The original files will not be deleted.

    Args:
        baseFolderPath (os.path): The path to the folder containing the debate files.
    """
    for filename in os.listdir(baseFolderPath):
        if filename.endswith(".txt"):
            file_path = os.path.join(baseFolderPath, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                lang = detect(content)
                # print(f"File '{filename}' has been detected to be in language '{lang}'.")

                # Create folder for the language if not existing already
                lang_folder = os.path.join(baseFolderPath, lang)
                if not os.path.exists(lang_folder):
                    os.makedirs(lang_folder)
                
                # Copy file to the appropriate folder
                new_file_path = os.path.join(lang_folder, filename)
                shutil.copy(file_path, new_file_path)
            
            except LangDetectException:
                print(f"Failed to detect language of '{filename}'.")