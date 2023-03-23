from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import multiprocessing

all_links=[]
start_time = datetime.now()
options = Options()
options.headless = True

#Find out how many pages there are of sold items
def get_number_of_pages():
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.andelemandele.lv/perles/#order:actual/sold:1/page:0")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.find("button", class_="btn paging__btn dropdown-toggle").text.split(" ")[-1]
    driver.delete_all_cookies()
    driver.close()
    return int(pages)


#Iterate through all pages of the website
def get_all_links():
    for i in range(int(get_number_of_pages())):
        #Create selenium driver for chrome that accesses website "www.andelemandele.lv"
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://www.andelemandele.lv/perles/#order:actual/sold:1/page:{i}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)

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
        print(f"All items added, total {len(all_links)}\n")
        
        driver.delete_all_cookies()
        driver.close()

    return all_links

def get_category(all_links):
    counter = 0
    categories = {}
    driver = webdriver.Chrome(options=options)
    #iterate each link and enter items page
    for link in all_links:
        driver.get(link)
        time.sleep(0.5)

        #Scrape the category data from the item
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            category1 = soup.find("div", class_="breadcrumb").find_all("a")[-3].text
            category2 = soup.find("div", class_="breadcrumb").find_all("a")[-2].text
        except:
            with open('error_log.txt', 'w', encoding="utf-8") as f:
                f.write(f"Local Error occured at get_category(): {link} \n Runtime: {datetime.now()-start_time} \n -----------------------------\n")
            pass
        try:
            category = f"{category1} / {category2}"
            if category in categories.keys():
                categories[category] += 1
            else:
                categories[category] = 1
            print(f"category: {category} added\n")
            counter += 1
            print(f"counter: {counter}\n")
        except:
            with open('error_log.txt', 'w', encoding="utf-8") as f:
                f.write(f"Local Error occured at get_category(): {link} \n Tried to get categories: {category1} and {category2} \n Runtime: {datetime.now()-start_time} -----------------------------\n")
            pass
        driver.delete_all_cookies()
    driver.close()
    print(f"{counter} items added in total\n")
    return categories

#----------------------MAIN----------------------
try:
    all_links = get_all_links()
    categories = get_category(all_links)

    with open('result.txt', 'w', encoding="utf-8") as f:
        f.write(f"{str(categories)}\n Runtime: {datetime.now() - start_time}")
except:
    with open('error_log.txt', 'w', encoding="utf-8") as f:
            f.write(f"Global Error: Error occured at: {datetime.now() - start_time}")




