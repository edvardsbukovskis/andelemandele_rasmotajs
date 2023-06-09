from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import concurrent.futures

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

def get_all_links(webdriver_pool, options):
    def fetch_links_for_page(args):
        i, webdriver_pool, options = args
        all_links = []
        driver = get_webdriver_instance(webdriver_pool, options)

        driver.get(f"https://www.andelemandele.lv/perles/#order:actual/sold:1/page:{i}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - (document.body.scrollHeight - 1))")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)

        # Get all elements from driver using beautifulsoup which have "article" tag and class "product-card no-user inactive applications thumbnail-ready" and store them in a list
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all("article", class_="product-card no-user inactive applications thumbnail-ready")

        # Get all links of sold items
        for product in products:
            item = product.find("figure")
            link = item.find("a")
            all_links.append("https://www.andelemandele.lv"+link.get('href'))
        
        driver.delete_all_cookies()
        release_webdriver_instance(webdriver_pool, driver)
        print(f"Page counter: {i}")
        return all_links

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        all_links_results = list(executor.map(fetch_links_for_page, [(i, webdriver_pool, options) for i in range(get_number_of_pages())]))

    # Flatten the list of lists to a single list of links
    all_links = [link for page_links in all_links_results for link in page_links]
    return all_links


def get_webdriver_instance(webdriver_pool, options):
    """
    If the webdriver_pool is empty, create a new webdriver instance and return it. If the webdriver_pool
    is not empty, pop the last element from the pool and return it
    
    :param webdriver_pool: A list of webdriver instances
    :param options: This is the ChromeOptions object that we created earlier
    :return: A webdriver instance
    """
    if not webdriver_pool:
        driver = webdriver.Chrome(options=options)
        return driver
    else:
        return webdriver_pool.pop()

def release_webdriver_instance(webdriver_pool, driver):
    """
    It takes a webdriver instance and appends it to the webdriver pool
    
    :param webdriver_pool: a list of webdriver instances
    :param driver: The webdriver instance to be released
    """
    webdriver_pool.append(driver)

def get_sold_product_data(args):
    """
    It takes a link, a webdriver pool and some options as arguments, then it gets the webdriver instance
    from the pool, gets the link, waits for 0.5 seconds, scrapes the category data from the item,
    deletes all cookies, releases the webdriver instance back to the pool, and returns the category and
    price
    
    :param args: (link, webdriver_pool, options)
    :return: A tuple of category and price
    """
    link, webdriver_pool, options = args

    driver = get_webdriver_instance(webdriver_pool, options)
    driver.get(link)
    time.sleep(0.5)

    # Scrape the category data from the item
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.delete_all_cookies()
    release_webdriver_instance(webdriver_pool, driver)
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
if __name__ == "__main__":
    start_time = datetime.now()
    options = Options()
    options.headless = True
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    workers = 4

    webdriver_pool = []
    all_links = get_all_links(webdriver_pool, options)
    
    # Create a thread pool and execute
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(get_sold_product_data, [(link, webdriver_pool, options) for link in all_links]))

    # Working with files
    # Load the existing JSON file or create an empty dictionary if the file does not exist
    try:
        with open('result.json', 'r', encoding="utf-8") as f:
            results_dict = json.load(f)
    except FileNotFoundError:
        results_dict = {"categories": {}}

        # Update the existing dictionary with new data
    for result in results:
        try:
            if result is not None:
                category, price = result
                if category in results_dict["categories"]:
                    results_dict["categories"][category]["prices"].append(price)
                else:
                    results_dict["categories"][category] = {"prices": [price]}
        except:
            with open('error_log.txt', 'a', encoding="utf-8") as f:
                f.write(f"Error saving to dict cat:{category}, price:{price}\n")
            continue

    # Add count of how many each category items there are
    for category in results_dict["categories"]:
        results_dict["categories"][category]["count"] = len(results_dict["categories"][category]["prices"])
        results_dict["avg_cat_price"] = sum(results_dict["categories"][category]["prices"]) / len(results_dict["categories"][category]["prices"])

    # Add runtime stamp and datetime stamp to dictionary
    results_dict["runtime"] = str(datetime.now() - start_time)
    results_dict["datetime"] = str(datetime.now())

    # Save the updated dictionary to the JSON file
    json_obj = json.dumps(results_dict, indent=1, ensure_ascii=False)
    with open('result.json', 'w', encoding="utf-8") as f:
        f.write(json_obj)