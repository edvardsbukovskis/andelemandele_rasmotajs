from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import multiprocessing


#Find out how many pages there are of sold items
def get_number_of_pages():
    driver.get("https://www.andelemandele.lv/perles/#order:actual/sold:1/page:0")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.find("button", class_="btn paging__btn dropdown-toggle").text.split(" ")[-1]
    driver.delete_all_cookies()
    return int(pages)


#Iterate through all pages of the website
def get_all_links():
    pages = 0
    for i in range(get_number_of_pages()):
        #Create selenium driver for chrome that accesses website "www.andelemandele.lv"
        driver.get(f"https://www.andelemandele.lv/perles/#order:actual/sold:1/page:{i}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - (document.body.scrollHeight - 1))")
        time.sleep(0.5)
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
        pages +=1
        print(f"All items added, pages:{pages} total items:{len(all_links)}\n")
        
        driver.delete_all_cookies()
    return all_links

def get_sold_product_data(all_links):
    counter = 0
    data = {}
    #iterate each link and enter items page
    for link in all_links:
        driver.get(link)
        time.sleep(0.5)

        #Scrape the category data from the item
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            category1 = soup.find("div", class_="breadcrumb").find_all("a")[-3].text
            category2 = soup.find("div", class_="breadcrumb").find_all("a")[-2].text
            price = int(soup.find("span", class_="product__price old-price").text.split(' ')[0])
        except:
            with open('error_log.txt', 'a', encoding="utf-8") as f:
                f.write(f"Local Error occured at get_sold_product_data(): {link} \nRuntime: {datetime.now()-start_time}\nDatetime: {datetime.now()}\n-----------------------------\n")
            pass
        try:
            category = f"{category1} | {category2}"
            if category in data["categories"].keys():
                data["categories"][category]["counter"] += 1
                data["categories"][category]["category_prices"].append(price)
            else:
                data["categories"][category] = {"counter":1, "category_prices":[price]}
                
            print(f"category: {category} added\n")
            counter += 1
            print(f"counter: {counter}\n")
        except:
            with open('error_log.txt', 'a', encoding="utf-8") as f:
                f.write(f"Local Error occured at get_sold_product_data(): {link}\nRuntime: {datetime.now()-start_time}\nDatetime: {datetime.now()}\n-----------------------------\n")
            pass
        driver.delete_all_cookies()
    print(f"{counter} items added in total\n")
    return data

#----------------------(__main__)----------------------
if __name__ == "__main__":
    start_time = datetime.now()
    all_links=[]
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    try:
        all_links = get_all_links()
        data = get_sold_product_data(all_links)
        driver.close()
        
        #serialize json for a dump
        data["Runtime"] = str(datetime.now() - start_time)
        data["Starttime"] = str(start_time)
        data["Endtime"] = str(datetime.now())
        json_obj = json.dumps(data, indent=1, ensure_ascii=False)

        with open('result.json', 'a', encoding="utf-8") as f:
            f.write(json_obj)
    
    except:
        with open('error_log.txt', 'a', encoding="utf-8") as f:
            f.write(f"Error occured at __main__: {datetime.now() - start_time}\nDatetime: {datetime.now()}\n-----------------------------\n")