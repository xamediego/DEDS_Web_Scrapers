from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

import Tools
from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit):
    amazon_data = sel_scrape_amazon(search_term, page_limit)

    return amazon_data


def sel_scrape_amazon(search_term, page_limit):
    data = {"reviews": [], "images": [], 'prices': [], 'titles': []}

    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, search_term, "https://www.amazon.nl")

    url = driver.current_url
    page_counter = 0

    while (page_counter != page_limit) & (check_next(driver, url)):
        url = get_next_url(driver)

        r_data = prod_page(driver)
        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']

        data['prices'] = data['prices'] + get_prices(driver)
        data['titles'] = data['titles'] + get_titles(driver)

        page_counter += 1

    driver.close()

    print('AMAZON SCRAPE END')
    get_scraped_data_size_info(data)

    return data


def initial_navigation(driver, search_term, site_link):
    Tools.load_page(driver, site_link, 30)

    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )

    search_box.send_keys(search_term)

    search_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    search_button.click()

    category_dropdown = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "searchDropdownBox"))
    )

    category_dropdown.send_keys("Kleding, schoenen en sieraden")

    search_box.submit()

    time.sleep(1)

    alles_check_box = driver.find_elements(By.CSS_SELECTOR, 'li[aria-label="Alles"]')
    alles_link = alles_check_box[0].find_elements(By.CSS_SELECTOR, 'a')
    link = alles_link[0].get_attribute('href')

    Tools.load_page(driver, link, 30)

    time.sleep(1)


def get_prices(driver):
    prices = []

    span_prices = driver.find_elements(By.CSS_SELECTOR, 'span.a-price-whole')

    for price in span_prices:
        prices.append(price.text)

    return prices


def get_titles(driver):
    titles = []

    product_tiles = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')

    for products in product_tiles:

        titles_span = products.find_elements(By.CSS_SELECTOR, 'span.a-size-base-plus.a-color-base.a-text-normal')

        if len(titles_span) > 0:
            titles.append(titles_span[0].text)

    return titles


def prod_page(driver):
    search_results = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')

    soup_result = []

    for result in search_results:
        html = result.get_attribute('innerHTML')
        soup_result.append(BeautifulSoup(html, 'html.parser'))

    return parse_page(driver, soup_result)


def parse_page(driver, soup_result):
    data = {"reviews": [], "images": []}

    for result in soup_result:
        a_tag = result.select_one('a.a-link-normal.s-no-outline')

        p_link = 'https://www.amazon.nl' + a_tag['href']

        try:
            r_data = get_data(driver, p_link)

            data['reviews'] = data['reviews'] + r_data['reviews']
            data['images'] = data['images'] + r_data['images']
        except:
            print('ERROR WHILE GETTING DATA')

    return data


def check_next(driver, link):
    Tools.load_page(driver, link, 30)

    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR,
                                         "a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator")

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR,
                                        "a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator")

    return search_result.get_attribute('href')


def get_data(driver, product_url):
    reviews = []
    images = []

    Tools.load_page(driver, product_url, 30)

    time.sleep(1)

    review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')

    try:
        for review_element in review_elements:
            review = review_element.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]')

            review_text = review.text

            reviews.append(review_text)
    except:
        print('ERROR WHILE PARSING REVIEW')

    image_elements = driver.find_elements(By.CSS_SELECTOR, 'img.a-dynamic-image')

    try:
        for image_element in image_elements:
            images.append(image_element.get_attribute("src"))
    except:
        print('ERROR WHILE PARSING SRC')

    return {"reviews": reviews, "images": images}
