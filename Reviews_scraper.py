import pandas as pd
from urllib.request import Request, urlopen
from selenium import webdriver
# conda install -c anaconda beautifulsoup4=4.6.0 
from bs4 import BeautifulSoup
import requests
import time
import numpy as np


reviews_url = pd.read_csv("Trip_advisor_URLs.csv")
reviews_url.loc[0]['Review_link'] 
Hotel_name = reviews_url.iloc[0]['Hotel Name'] 
City_name =  reviews_url.iloc[0]['City'] 

review_Hotel = pd.DataFrame(columns=['Hotel_name'])
review_city  = pd.DataFrame(columns=['city_name'])


Final_data = pd.DataFrame()
i=0

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

for i in range(1):
    browser = webdriver.Firefox(executable_path='geckodriver-v0.26.0-win64/geckodriver')
    
    browser.get("https://www.google.com?hl=en")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")	
    browser.get(reviews_url.loc[i]['Review_link'] )  
    buttons = browser.find_elements_by_xpath('//span[@class="taLnk ulBlueLinks" and contains(text(),"More")]')
    #croll_shim(browser,buttons) 

    #try:
    for button in buttons:
        scroll_shim(browser,button)
        degree.click()
    #except:
    #a = 1

    for second in range(100):
        if second >=5:
            break
        else:
           time.sleep(0.5)    

    html_source = browser.page_source  
    print(html_source)
    soup_ans = BeautifulSoup(html_source, "lxml")
    review_date = soup_ans.find_all("span",{"class":"ratingDate relativeDate"})
    review_title = soup_ans.find_all("div",{"class":"quote"})
    review_content = soup_ans.find_all("div",{"class":"innerBubble"})
    review_rating = soup_ans.find_all("div",{"class":"rating reviewItemInline"})

    browser.quit()

    date_rating_review = pd.DataFrame(columns =['date_rating'])
    title_review= pd.DataFrame(columns = ['review_title'])
    content_review = pd.DataFrame(columns = ['text'])
    rating_review = pd.DataFrame(columns = ['rating'])

    k=0
    for item in review_date:
        a = str(item)
        print (a)
        date_rating_review.loc[k,'date_rating'] = a
        k = k+1

    l = 0
    for item in review_title:
        a = item.text
        #print (a)
        title_review.loc[l,'review_title'] = a
        l = l+1

    m = 0
    for item in review_content:
        a = item.text
        #print (a)
        content_review.loc[m,'text'] = a
        m = m+1

    p=0
    for item in review_rating:
        a = item
        #print (a)
        rating_review.loc[p,'rating'] = a
        p = p+1

    # Combine dataframes 
    Combined_data = pd.concat([review_city,review_Hotel,date_rating_review,title_review,content_review,rating_review], axis=1)
    Final_data = pd.concat([Final_data, Combined_data])
    Final_data = Final_data.reset_index(drop=True)
    print(i)

Final_data.to_csv('Trip_advisor_results.csv')
