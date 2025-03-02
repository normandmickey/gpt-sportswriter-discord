import os, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

# get the API KEY here: https://developers.google.com/custom-search/v1/overview
GSE_API_KEY=os.environ.get("GSE_API_KEY")
# get your Search Engine ID on your CSE control panel
SEARCH_ENGINE_ID = "165d6350f51dc4e9f"

chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless=new") # for Chrome >= 109
# chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works
#GOOGLE_API_KEY="AIzaSyAtLLYVb_lvHlmURnhI3N3ctgiXn5hmjrc"
#GOOGLE_CX_KEY="165d6350f51dc4e9f"
#GOOGLE_CSE_ID="165d6350f51dc4e9f"

# the search query you want
query = "Prediction Murray St Racers VS Belmont Bruins 2025-03-02"
# using the first page
page = 1
# constructing the URL
# doc: https://developers.google.com/custom-search/v1/using_rest
# calculating start, (page=2) => (start=11), (page=3) => (start=21)
start = (page - 1) * 3 + 1
url = f"https://www.googleapis.com/customsearch/v1?key={GSE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"

# make the API request
data = requests.get(url).json()

# Function to remove tags
def remove_tags(html):

    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

# Function to remove tags
def scrape_body(html):

    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    tag = soup.body
    return tag

# get the result items
search_items = data.get("items")
# iterate over 10 results found
for i, search_item in enumerate(search_items, start=1):
    try:
        long_description = search_item["pagemap"]["metatags"][0]["og:description"]
    except KeyError:
        long_description = "N/A"
    # get the page title
    ##title = search_item.get("title")
    # page snippet
    ##snippet = search_item.get("snippet")
    # alternatively, you can get the HTML snippet (bolded keywords)
    ##html_snippet = search_item.get("htmlSnippet")
    # extract the page url
    link = search_item.get("link")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    html_cont = driver.page_source
    print(remove_tags(html_cont))
    # print the results
    #print("="*10, f"Result #{i+start-1}", "="*10)
    #print("Title:", title)
    #print("Description:", snippet)
    #print("Long description:", long_description)
    print("URL:", link, "\n")