import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from Tools import get_scraped_data_size_info


def scrape_full(search_term, bol_category, page_limit):
    bol_data = scraper(search_term, bol_category, page_limit)

    return bol_data


def scraper(search_value, selected_category, page_limit):
    data = {'reviews': [], 'images': [], 'prices': []}

    driver = webdriver.Edge()

    initial_navigation(driver, 'https://www.bol.com/nl/nl/s/', search_value, selected_category, 'Kleding')

    url = driver.current_url
    page_counter = 0

    while (page_counter != page_limit) & (check_next(driver, url)):

        url = get_next_url(driver)

        r_data = prod_page(driver)
        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']


        data['prices'] = data['prices'] + get_prices(driver)

        get_scraped_data_size_info(data)

        page_counter += 1

    return data


def initial_navigation(driver, site_url, search_value, selected_category, sub_category):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    params = {'searchtext': search_value, 'sort': 'rating1'}

    response = requests.get(site_url, params=params, headers=hdr, timeout=15)

    driver.get(response.url)

    time.sleep(1)

    click_consent_button(driver)

    categorized_link = get_category_link(driver, selected_category)

    driver.get(categorized_link)

    time.sleep(1)

    categorized_link = get_category_link(driver, sub_category)

    driver.get(categorized_link)

    time.sleep(1)

    categorized_link = get_category_link(driver, 'Jassen')

    driver.get(categorized_link)

    time.sleep(1)


def get_category_link(driver, selected_category):
    link = ''

    cats = driver.find_elements(By.CSS_SELECTOR, 'a.px_listpage_categoriesleft_click')

    for category in cats:
        cat = category.text.split(" ")[0]

        if cat == selected_category:
            link = category.get_attribute('href')
            break

    return link


def prod_page(driver):
    search_results = driver.find_elements(By.CSS_SELECTOR, "li[class*='product-item--row js_item_root']")

    soup_result = []

    for result in search_results:
        html = result.get_attribute('innerHTML')
        soup_result.append(BeautifulSoup(html, 'html.parser'))

    return parse_page(driver, soup_result)


def parse_page(driver, soup_result):
    data = {"reviews": [], "images": []}

    for result in soup_result:
        product_links = result.find('a', {
            'class': 'product-title px_list_page_product_click list_page_product_tracking_target'})

        p_link = 'https://www.bol.com' + product_links['href']

        r_data = get_data(driver, p_link, data['reviews'])

        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']

    return data


def get_data(driver, product_url, old_reviews):
    driver.get(product_url)

    time.sleep(1)

    reviews = scrape_review_bodies(driver, old_reviews)
    images = scrape_image_links(driver)

    return {"reviews": reviews, "images": images}


def scrape_review_bodies(driver, old_reviews):
    # Find the product reviews
    product_image_ref = driver.find_elements(By.CSS_SELECTOR, 'li.review.js-review')

    soup_result = []

    for result in product_image_ref:
        html = result.get_attribute('innerHTML')
        soup_result.append(BeautifulSoup(html, 'html.parser'))

    # Loops trough ze reviews
    return get_review_bodies(soup_result, old_reviews)


def get_review_bodies(review_container, old_reviews):
    reviews = []

    for r_data in review_container:
        r_body = r_data.find('p', {'data-test': 'review-body'})

        if r_body:
            review_text = str(r_body.text.strip())

            if review_text not in old_reviews:
                reviews.append(review_text)

    return reviews


def scrape_image_links(driver):
    # Find the product image
    product_image_ref = driver.find_elements(By.CSS_SELECTOR, 'img.js_selected_image.has-zoom')

    soup_result = []

    for result in product_image_ref:
        html = result.get_attribute('innerHTML')
        soup_result.append(BeautifulSoup(html, 'html.parser'))

    # Loops trough ze images
    return get_image_links(soup_result)


def get_image_links(product_image_ref):
    images = []

    for img in product_image_ref:
        # gets src for filename
        src = img.get('src')

        if src not in images:
            images.append(src)

    return images


def get_prices(driver):
    prices = []

    price_spans = driver.find_elements(By.CSS_SELECTOR, 'span[data-test="price"]')

    for price in price_spans:
        prices.append(price.text)

    return prices


def check_next(driver, link):
    driver.get(link)

    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label="volgende"]')

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="volgende"]')

    return search_result.get_attribute('href')


def click_consent_button(driver):
    consent_button = driver.find_element(By.ID, 'js-first-screen-accept-all-button')

    consent_button.click()
