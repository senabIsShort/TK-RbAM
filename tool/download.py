from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import os

def downloadDiscussions(discussionUrlIds : list[str], kialoUsername : str, secret : str, downloadPath : os.path = os.path.abspath("../rawData/debates")):
  """Download discussions from Kialo using Selenium.
  This function logs into Kialo and downloads discussions based on the provided URL IDs.
  The discussions are saved as text files in the specified download path.
  The function creates the download path if it does not exist.

  Args:
      discussionUrlIds (list[str]): List of discussion URL IDs to download
      kialoUsername (str): Username for Kialo account
      secret (str): Password for Kialo account
      downloadPath (os.path, optional): Path to save downloaded discussions. Defaults to "../rawData/debates".
  """
  path = downloadPath

  if not os.path.exists(path):
    os.makedirs(path)

  prefs = {"download.default_directory": path }
  options = Options()
  options.add_experimental_option("prefs", prefs)
  driver = webdriver.Chrome(options = options)


  driver.get("https://www.kialo.com/login")

  #Login
  id          = driver.find_element(By.ID, "emailOrUsername")
  password    = driver.find_element(By.ID, "password")
  loginButton = driver.find_element(By.CLASS_NAME, "login-form__submit")
  id.send_keys(kialoUsername)
  password.send_keys(secret)

  loginButton.click()

  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'home-page-section__header')))


  for urlId in tqdm(discussionUrlIds):
    driver.get("https://www.kialo.com/export/" + urlId + ".txt")
    time.sleep(1.5)