from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import multiprocessing
from functools import partial



def get_number_of_pages():
    """
    It gets the number of pages from the website, and returns it as an integer
    :return: The number of pages in the website.
    """
    driver.get("https://www.andelemandele.lv/perles/#order:actual/sold:1/page:0")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.find("button", class_="btn paging__btn dropdown-toggle").text.split(" ")[-1]
    driver.delete_all_cookies()
    return int(pages)

def get_all_links():
    """
    It creates a selenium driver for chrome that accesses website "www.andelemandele.lv" and gets all
    links of sold items and stores them in a list.
    :return: A list of all links of sold items
    """
    all_links=[]
    pages = 0
    for i in range(1):
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

        #Get all links of sold items
        for product in products:
            item = product.find("figure")
            link = item.find("a")
            all_links.append("https://www.andelemandele.lv"+link.get('href'))
        pages +=1
        print(f"All items added, pages:{pages} total items:{len(all_links)}\n")
        
        driver.delete_all_cookies()
    return all_links

def get_sold_product_data(link):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get(link)
    time.sleep(0.5)

    #Scrape the category data from the item
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.delete_all_cookies()
    driver.close()
    try:
        category1 = soup.find("div", class_="breadcrumb").find_all("a")[-3].text
        category2 = soup.find("div", class_="breadcrumb").find_all("a")[-2].text
        price = float(soup.find("span", class_="product__price old-price").text.split(' ')[0])
        category = f"{category1} | {category2}"
    except:
        with open('error_log.txt', 'a', encoding="utf-8") as f:
            f.write(f"Local Error occured at get_sold_product_data():{link} \nRuntime: {datetime.now()-start_time}\nDatetime: {datetime.now()}\n-----------------------------\n")
        return None
    
    print(f"category: {category} added\n")
    return (category, price)


#----------------------(__main__)----------------------

# The above code is a web scraper that is scraping the sold products from the website.
if __name__ == "__main__":
    start_time = datetime.now()
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    all_links = get_all_links()
    driver.close()

    #Create a multiprocess pool and execute
    pool = multiprocessing.Pool(processes=4)
    results = pool.map(get_sold_product_data, all_links)
    pool.close()
    pool.join()
    
    results_dict = {"categories":{}}
    for result in results:
        try:
            if result is not None:
                category, price = result
                if category in results_dict["categories"]:
                    results_dict["categories"][category]["prices"].append(price)
                else:
                    results_dict["categories"][category]={"prices":[price]}
        except:
            with open('error_log.txt', 'a', encoding="utf-8") as f:
                f.write(f"Error saving to dict cat:{category}, price:{price}\n")
            continue
        
    #Add count of how many each category item ther was
    for category in results_dict["categories"]:
        results_dict["categories"][category]["count"] = len(results_dict["categories"][category]["prices"])  
    
    #Add runtime stamp and datetime stamp to dictionary
    results_dict["runtime"] = str(datetime.now()-start_time)
    results_dict["datetime"] = str(datetime.now())
        
    print(results_dict)          