import os
import re
import sys
import json
import time
import datetime
import platform
from docopt import docopt
from tqdm import tqdm 
from time import sleep
import pandas as pd
from pandas.io.json import json_normalize
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

def initBrowser(headless=False):
    if "Windows" in platform.system():
        chrome_path = "driver/chromedriver.exe"
    else:
        chrome_path = "driver/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--disable-features=NetworkService")
    if headless:
        chrome_options.add_argument('headless')
    return webdriver.Chrome(options=chrome_options,executable_path=chrome_path)

def tabNTimes(N=2):
    actions = ActionChains(browser) 
    for _ in range(N):
        actions = actions.send_keys(Keys.TAB)
    actions.perform()
    
def sleepBar(seconds):
    for i in tqdm(range(seconds)):
        sleep(1)
def clickNTimes(el, n=1):
    for i in range(n):
        el.click()
        logging.info(f"clicking on ... {el.text}")
        sleepBar(1)
        scrollToFeedback()
        try:
            el.find_element_by_xpath("//*[@aria-expanded='true']").click()
        except:
            pass
        sleepBar(1)
def scrollToFeedback():
    
    el = browser.find_element_by_xpath("//div[@class='kno-ftr']//div/following-sibling::a[text()='Feedback']")
    actions = ActionChains(browser)
    actions.move_to_element(el).perform()
    browser.execute_script("arguments[0].scrollIntoView();", el)
    actions.send_keys(Keys.PAGE_UP).perform()
    sleepBar(1)

if __name__=="__main__":
	args = list(sys.argv)
	query = args[1]
	file_name = args[2]
	#intialise the browser will open a tab in chrome
	browser = initBrowser()
	browser.get("https://www.google.com?hl=en")
	searchbox = browser.find_element_by_xpath("//input[@aria-label='Search']")
	searchbox.send_keys(query)
	sleepBar(2)
	tabNTimes()
	searchbtn = browser.find_elements_by_xpath("//input[@aria-label='Google Search']")
	searchbtn[-1].click()
	inital_results = browser.find_elements_by_xpath("//span/following-sibling::div[contains(@class,'match-mod-horizontal-padding')]")
	browser.execute_script('document.getElementById("searchform").style.display = "none";')
	scrollToFeedback()
	#generate more questions
	for qa in inital_results:
		scrollToFeedback()
		sleepBar(1)
		clickNTimes(qa) 

	final_ques = browser.find_elements_by_xpath("//span/following-sibling::div[contains(@class,'match-mod-horizontal-padding')]")
	for qa in final_ques:
		scrollToFeedback()
		qa.click()

	final_para = browser.find_elements_by_xpath("//div[contains(@class,'kno-aoc')]")

	results = []
	for q,c in zip(final_ques,final_para):
	    context = c.text
	    question = q.text
	    results.append({
	        "context":context,
	        "question":question
	        
	    })

	final_df = pd.DataFrame(results)
	final_df.to_csv(file_name)
	browser.close()
	    










