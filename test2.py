from bs4 import BeautifulSoup
from selenium import webdriver
import time
from datetime import datetime
import multiprocessing

all_links=[]
start_time = datetime.now()

#Find out how many pages there are of sold items
def get_number_of_pages():
    driver = webdriver.Chrome()
    driver.get("https://www.andelemandele.lv/perles/#order:actual/sold:1/page:0")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.find("button", class_="btn paging__btn dropdown-toggle").text.split(" ")[-1]
    return int(pages)


#Iterate through all pages of the website
def get_all_links():
    for i in range(1):
        #Create selenium driver for chrome that accesses website "www.andelemandele.lv"
        driver = webdriver.Chrome()
        driver.get(f"https://www.andelemandele.lv/perles/#order:actual/sold:1/page:{i}")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        #Get all elements from driver using beautifulsoup which have "article" tag and class "product-card no-user inactive applications thumbnail-ready" and store them in a list
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all("article", class_="product-card no-user inactive applications thumbnail-ready")

        #Get only figure tag
        all_items = []
        for product in products:
            item = product.find("figure")
            all_items.append(item)

        #Get only href links
        for item in all_items:
            link = item.find("a")
            all_links.append("https://www.andelemandele.lv"+link.get('href'))

    return all_links

def get_category(link):
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(1)

    #Scrape the category data from the item
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        category1 = soup.find("div", class_="breadcrumb").find_all("a")[-3].text
        category2 = soup.find("div", class_="breadcrumb").find_all("a")[-2].text
        category = f"{category1} -> {category2}"
        return category
    except:
        with open('error_log.txt', 'a', encoding="utf-8") as f:
            f.write(f"Error occured at: {link}\n")
        return None

#----------------------CATEGORY SEARHING----------------------
all_links = get_all_links()
pool = multiprocessing.Pool(processes=2)
results = pool.map(get_category, all_links)
pool.close()
pool.join()

categories = {}
for result in results:
    for category in result.keys():
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 0

with open('result.txt', 'w', encoding="utf-8") as f:
    f.write(f"{str(categories)}\n Runtime: {datetime.now() - start_time}")




