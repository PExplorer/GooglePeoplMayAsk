<pre>
# GooglePeoplMayAsk
This repo contains the code for scrapping the Question and context from google people may ask


Step 1 

Download chrome driver for your mac/linux/windows from link below
<a href="https://chromedriver.storage.googleapis.com/index.html">chromedriver</a>
Place the downloaded chrome drive into driver folder.

Step 2 :Scrape the results

python people_also_ask.py 'Albert Eienstien' albert_eienstien.csv
Results are saved as csv

Make necessary changes to file to include more results .

<h1>Code is written using selenium libraries for python.</h1>

</pre>

<pre>

Possible UseCases
1) Improving the reading comprehension model (squad is the only dataset used currently)
2) Faq Generation
3) Any Natural language gneration usecases


</pre>
