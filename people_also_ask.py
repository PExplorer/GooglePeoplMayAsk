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
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException#, ElementClickInterceptedException

import lxml
from lxml.html.clean import Cleaner
import difflib 
import time

def get_web_link(answer):
    start = 'https'
    end = 'Search'
    web_link = 'https'+answer[answer.find(start)+len(start):answer.rfind(end)]
    web_link = web_link.replace(' › ','/')
    if len(web_link)<1:
        return "No link"
    return web_link  

def get_context(web_link,answer):
    browser = webdriver.Firefox(executable_path='geckodriver-v0.26.0-win64/geckodriver')
    browser.get(web_link)
    html_source = browser.page_source
    get_context= BeautifulSoup(html_source, "lxml")
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True 

    web_page_text = ''

    for element in get_context:
        element_string= lxml.html.document_fromstring(str(element))
        page_text = lxml.html.tostring(cleaner.clean_html(element_string))
        page_text = re.sub("<.*?>"," ", str(page_text))     
        web_page_text = web_page_text + " " + page_text 
    browser.close()
    matcher = difflib.SequenceMatcher(None,web_page_text,answer)
    match = matcher.find_longest_match(0,len(web_page_text),0,len(answer))
    if match.a>1000:
        start_context = match.a -999
    else:
        start_context = 0
        
    if len(web_page_text)>start_context + 2000:
        end_context = start_context + 2000
    else:
        end_context = len(web_page_text)-1

    context = web_page_text[start_context:end_context]
    return context


def initBrowser(headless=False):
    if "Windows" in platform.system():
        chrome_path = "driver/chromedriver.exe"
    else:
        chrome_path = "driver/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--disable-features=NetworkService")
    if headless:
        chrome_options.add_argument('headless')
    return webdriver.Chrome(executable_path=chrome_path)


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
        logging.info("clicking on ... {el.text}")
        sleepBar(1)
        scrollToFeedback()
        try:
            el.find_element_by_xpath("//*[@aria-expanded='true']").click()
        except:
            pass
        sleepBar(1)
        
def scroll_shim(passed_in_driver, object):
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    passed_in_driver.execute_script(scroll_by_coord)
    passed_in_driver.execute_script(scroll_nav_out_of_way)
        
def scrollToFeedback():   
    el = browser.find_element_by_xpath("//div[@class='kno-ftr']//div/following-sibling::a[text()='Feedback']")
    scroll_shim(browser,el)
    actions = ActionChains(browser)
    #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    browser.set_window_size(3000,900)
    actions.move_to_element(el).perform()
    browser.execute_script("arguments[0].scrollIntoView();", el)
    actions.send_keys(Keys.PAGE_UP).perform()
    sleepBar(1)
    

if __name__=="__main__":
    
    #for i in range(len(query_list)):

    i =100
    query = 'who sings the song in fifty shades of grey'
    print(query)
    print(i)

    file_name = "file_"+ str(i) + '.csv'    
    browser = webdriver.Firefox(executable_path='geckodriver-v0.26.0-win64/geckodriver')
    browser.get("https://www.google.com?hl=en")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    browser.set_window_size(3000,900)

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
    for q,a in zip(final_ques,final_para):
        answer = a.text
        question = q.text

        results.append({
            "answer":answer,
            "question":question
        })
    browser.close()
    results_df = pd.DataFrame(results)
    results_df.to_csv(file_name)

    final_results = []
    for k in range(len(results)):
        sleepBar(2)
        answer = results[k]['answer']
        question = results[k]['question']

        try:
            web_link = get_web_link(answer).replace('\n','')
            context  = get_context(web_link,answer)
            print(context[0:100])
        except:
            web_link = ""
            context = ""        
        final_results.append({
            "context":context,
            "question":question,
            "answer":answer,
            "web_link":web_link
        })

    final_file_name ="final_" + file_name 
    final_df = pd.DataFrame(final_results)
    final_df.to_csv(file_name)

    
