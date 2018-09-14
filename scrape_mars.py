from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()

    mars_data_dict = {}

    # NASA Mars News Site Scraping Segment

    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find('ul', class_="item_list")

    news_title = articles.find('div', class_="content_title").text

    news_p = articles.find('div', class_="article_teaser_body").text

    mars_data_dict["news_title"] = news_title
    mars_data_dict["news_p"] = news_p

    # NASA Featured Mars Images scraping segment

    # Navigate to appropriate elements using splinter

    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # Use splinter to click the full image button in order to retrieve appropriate url
    browser.click_link_by_partial_text('FULL IMAGE')

    # Use time.sleep to allow the html a second to load before trying to use Soup on it

    time.sleep(10)

    # Use beautiful soup to read html page

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Find the button classes to retrieve url component
    pic = soup.find('div', class_="buttons")

    # Isolate both buttons and their 'a' tags
    article_link = pic.find_all('a')

    # Use iterator to separate the 'a' tags, only take the relevant value and concatenate it with url to create
    # complete url for Splinter navigation
    for link in article_link:
        if link["href"] != "#":
            new_url = "https://www.jpl.nasa.gov/" + link["href"]

    # Use the retrieved url to navigate to the article page
    browser.visit(new_url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    image = soup.find('figure', class_="lede").a["href"]

    featured_image_url = "https://www.jpl.nasa.gov/" + image

    mars_data_dict["featured_image_url"] = featured_image_url

    # Mars Twitter Weather Data scraping segment

    # Scraping Mars weather data from the Mars weather twitter
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    # Set the html value for beautiful soup, and then parse the html page

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Get all tweets using the div class "tweet"

    all_tweets = soup.find_all('div', class_="tweet")

    # Iterate through all retrieved div containers

    for tweet in all_tweets:

        # Find the element of the tweet that contains the text
        tweet_content = tweet.find('div', class_="js-tweet-text-container")

        # Access the text of that element
        tweet_text = tweet_content.p.text
    
        # Split the returned string so that it can be compared and the appropriate value can be retrieved
        tweet_compare = tweet_text.split(" ")
    
        # Compare the first word of every tweet, as every weather tweet begins with the word "Sol", to prevent the scraper
        # from retrieving the text of one of the twitter page's non-weather tweets
        if tweet_compare[0] == "Sol":
            mars_weather = tweet_text
            break

    mars_data_dict["mars_weather"] = mars_weather

    # Space Facts scraping segment

    # Using pandas html reader to retrieve table from space facts web page
    url = "http://space-facts.com/mars/"

    # Retrieve all tables from the page
    table = pd.read_html(url)

    # Take the first (and only) table from the returned list
    df = table[0]

    # Rename the columns to make it look nicer
    df.columns = ['Mars Planet Profile','Facts']

    # Render the dataframe as an html table string
    html_df = df.to_html()

    mars_data_dict["fact_table"] = html_df

    # Mars Hemispheres scraping segment

    # Scraping the USGS Astrogeology website for Mars hemispheres pictures

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    # Create list for storing dictionaries

    hemisphere_image_urls = []

    # Visit the initial search page and collect all hemisphere titles

    html = browser.html
    soup = BeautifulSoup(html,"html.parser")

    items = soup.find_all('div', class_="description")

    # Iterate through the list and capture all relevant values

    for item in items:
    
        # Get the hemisphere title
        header = item.a.h3.text
    
        # Split the header so that the "Enhanced" at the end of the string can be removed, and so the first word can be
        # used to click the relevant link
        header_split = header.split(" ")
    
        # Use a comparative to determine if the string is three or four words long
        if len(header_split) == 4:
        
            # Rebuild the string and save to a variable, excluding the word "enhanced"
            title_string = header_split[0] + " " + header_split[1] + " " + header_split[2]
        
        else:
        
            # Rebuild the string and save to a variable, excluding the word "enhanced"
            title_string = header_split[0] + " " + header_split[1]
        
        # Using the first word of the title, click to that hemisphere's page
        browser.click_link_by_partial_text(header_split[0])

        # Use Splinter & BeautifulSoup to read the webpage
        html = browser.html
        soup = BeautifulSoup(html,"html.parser")

        # Get the relevant div class containing the link to the picture
        pictures = soup.find('div', class_="downloads")

        # Retrieve the picture link and save to a variable
        picture_link = pictures.ul.li.a["href"]

        # Create a temporary dictionary that contains the title string and picture link
        temp_dict = {
            "title":title_string,
            "img_url":picture_link
        }
    
        # Append the temporary dictionary to the list created earlier
        hemisphere_image_urls.append(temp_dict)
    
        # Click back to the search page so that the next hemisphere scrape can be performed
        browser.click_link_by_partial_text("Back")
    
    # Append the image urls dictionary to the main dictionary
    mars_data_dict["mars_image_urls"] = hemisphere_image_urls

    # Lastly, return the results of the scraping
    return mars_data_dict