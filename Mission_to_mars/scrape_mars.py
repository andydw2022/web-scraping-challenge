from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pymongo
import pandas as pd

def scrape_info():
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    #
    #Part 1 : Get Mars headlines from "https://redplanetscience.com/
    #---------------------------------------------------------------
    # Visit Mars News Site
    url = "https://redplanetscience.com/"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Get the latest news title and paragraph text from mars site
    news_title = soup.find('div', class_='content_title').text

    # Get the min avg temp
    news_p = soup.find('div', class_='article_teaser_body').text

    # Store data in a dictionary
    mars_headlines = {
         "headline": news_title,
         "paragraph": news_p
     }
 
    print(f"News title : {news_title}")
    print(f"News paragraph : {news_p}")

    #
    #Part 2 : Get Mars space images from "https://spaceimages-mars.com/
    #---------------------------------------------------------------
    # Visit JPL Mars Space Images - Featured Image
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    url = "https://spaceimages-mars.com"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Find the src for the Featured Space Image
    relative_image_path = soup.find('img',class_='headerimage fade-in')
    relative_image_path=relative_image_path.attrs['src']
    featured_image_url = url + '/' + relative_image_path

    mars_images = {
        "relative_image_path": relative_image_path,
        "featured_image_url": featured_image_url
     }

    #
    #Part 3 : Get Mars facts from "https://galaxyfacts-mars.com/
    #---------------------------------------------------------------
    # Visit Mars Facts webpage
    url = "https://galaxyfacts-mars.com"
    time.sleep(1)
    
    # Scrape page into Soup
    tables = pd.read_html(url)
    tables
    
    type(tables)
    df = tables[0]
    df.head()
    
    cols = list(df.columns)
    df.rename(columns={'0':'','1':'','2':''})
    df=df.reset_index()

    
    #Convert dataframe to HTML table
    df.columns = df.iloc[0] 
    df = df[1:]
    mars_facts_html_table = df.to_html(classes='table table-stripped')  
    #
    #Part 4 : Get Mars hemispheres data from "https://marshemispheres.com"
    #---------------------------------------------------------------
    # Visit Mars Facts webpage
    #Mars Hemispheres
    url = "https://marshemispheres.com"
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')
    #soup
    # Examine the results, then determine element that contains sought info
    # results are returned as an iterable list
    results = soup.find_all('div', class_='item')
# Loop through returned results
    idx=-1
    hemisphere_image_urls=[]
    hemisphere_title=[]
    for result in results:
        # Error handling
        try:      
            title = result.find('h3').text
            # Identify and return high resolution image url
            img_url = result.find_all('img')[0]["src"]
           
            link = result.a['href']           
            # Run only if title, img_url, and link are available
            idx=idx+1
            if (title and img_url and link):
             # Print results
                print('-------------')
                title=title.replace(' Hemisphere Enhanced','')
                title=title.replace(' ','_')
                if title=="Cerberus":
                  img_url="full.jpg"
                else:
                  img_url=title+"_enhanced-full.jpg"  
                img_url=(img_url.replace(' ','_'))
                img_url=img_url.lower()
                print(title)
                img_url=url+"/images/"+img_url
                print(img_url)
                # Dictionary to be inserted as a MongoDB document
                hemisphere_image_urls.append (img_url)
                hemisphere_title.append (title)
        except Exception as e:
            print(e)

        mars_data = {
            "headline": news_title,
            "paragraph": news_p,
            "relative_image_path": relative_image_path,
            "featured_image_url": featured_image_url,
            "mars_facts": mars_facts_html_table,
            "mars_hemisphere_title": hemisphere_title,
            "mars_hemisphere_img_url":hemisphere_image_urls
        }

    # Quit the browser
    browser.quit()

    # Return results
    return mars_data
    
