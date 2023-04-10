import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

import Tools
from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit, review_page_limit):
    print('Deca scrape')
    deca_data = start_scraper(search_term, page_limit, review_page_limit)

    return deca_data


def initial_navigation(driver, site_url, search_value):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    site_url = site_url + f'search?Ntt={search_value}'

    response = requests.get(site_url, headers=hdr, timeout=15)

    Tools.load_page(driver, response.url, 30)

    time.sleep(1)

    click_consent_button(driver)


def start_scraper(search_value, page_limit, review_page_limit):
    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, 'https://www.decathlon.nl/', search_value)

    return product_page_catalog_loop(driver, page_limit, review_page_limit)


def product_page_catalog_loop(driver, page_limit, review_page_limit):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles' : []}

    page_counter = 0
    url = driver.current_url

    try:
        while (page_counter != page_limit) & (check_next(driver, url)):

            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

            # Get review/images from item page
            product_data = get_product_data(driver, review_page_limit)

            if product_data:
                data['reviews'] = data['reviews'] + product_data['reviews']
                data['images'] = data['images'] + product_data['images']
                data['prices'] = data['prices'] + product_data['prices']
                data['titles'] = data['titles'] + product_data['titles']
            # Navigate to next page
            # driver.get(url)
            Tools.load_page(driver, url, 30)

            next_button = get_next_button(driver)

            time.sleep(1)

            next_button.click()
            time.sleep(4)

            url = driver.current_url

            page_counter += 1
    except:
        print('ERROR IN DECA PAGE LOOP')

    driver.close()

    print('DECA SCRAPE END')
    get_scraped_data_size_info(data)

    return data


def get_product_data(driver, review_page_limit):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles' : []}

    # Get review/images from item page

    # Gets all prices on the catalog page
    data['prices'] = data['prices'] + get_prices(driver)
    data['titles'] = data['titles'] + get_titles(driver)
    product_soup = get_catalog_soup(driver)

    # Loops trough all the products shown on the catalog page and adds obtained data
    r_data = product_loop(driver, product_soup, review_page_limit)

    data['reviews'] = data['reviews'] + r_data['reviews']
    data['images'] = data['images'] + r_data['images']

    get_scraped_data_size_info(data)

    return data

def get_titles(driver):
    titles = []

    product_tiles = driver.find_elements(By.CSS_SELECTOR, 'div.vtmn-flex.vtmn-flex-col.vtmn-items-center.vtmn-relative.vtmn-overflow-hidden.vtmn-text-center.vtmn-z-0.dpb-holder.svelte-2ckipo')

    for product in product_tiles:
        title_span = product.find_elements(By.CSS_SELECTOR, 'h2.vtmn-p-0.vtmn-m-0.vtmn-text-sm.vtmn-font-normal.vtmn-overflow-hidden.vtmn-text-ellipsis.svelte-1l3biyf')

        if len(title_span) > 0:
            titles.append(title_span[0].text)

    return titles

def get_prices(driver):
    prices = []

    span_prices = driver.find_elements(By.CSS_SELECTOR, 'span[aria-label="price"]')

    for price in span_prices:
        prices.append(price.text)

    return prices


def get_catalog_soup(driver):
    product_list = driver.find_element(By.CSS_SELECTOR, "div.product-list.pl-list.js-first.svelte-1wkvbov")
    html = product_list.get_attribute('innerHTML')
    return BeautifulSoup(html, 'html.parser')


def check_next(driver, link):
    Tools.load_page(driver, link, 30)

    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Next product list page"]')

    return len(search_result) > 0


def get_next_button(driver):
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next product list page"]')

    return next_button


def click_consent_button(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")

    for button in buttons:
        if button.text == 'Akkoord en sluiten':
            button.click()
            break


def product_loop(driver, current_page_soup, review_page_limit):
    data = {'reviews': [], 'images': [], 'prices': []}

    div_element = current_page_soup.find_all('div', {
        'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

    for prod_div in div_element:
        try:
            p_data = p_s(driver, prod_div, review_page_limit)
            data['reviews'] = data['reviews'] + p_data['reviews']
            data['images'] = data['images'] + p_data['images']
        except:
            print('ERROR WHILE RETRIEVING DATA')

    return data


def p_s(driver, prod_soup, review_page_limit):
    data = {'reviews': [], 'images': []}

    link = prod_soup.find('a')

    product_link = link['href']

    link = f"https://www.decathlon.nl/{product_link}"

    # Get product images
    time.sleep(0.5)

    Tools.load_page(driver, link, 30)

    time.sleep(1)

    data['images'] = data['images'] + get_images(driver)

    # Get product reviews
    review_link = link.replace("nl//p/", "nl/r/")

    Tools.load_page(driver, review_link, 30)
    time.sleep(1)

    data['reviews'] = data['reviews'] + parse_all_reviews(driver, review_page_limit)

    return data


def get_images(driver):
    images = []

    image_div = driver.find_elements(By.CSS_SELECTOR, 'div.product-images.svelte-175mzv1')

    if len(image_div) > 0:
        thumbnail_slider = driver.find_elements(By.ID, 'thumbnails-slider')
        if len(thumbnail_slider) > 0:
            thumbnail_buttons = thumbnail_slider[0].find_elements(By.CSS_SELECTOR, 'button')

            for button in thumbnail_buttons:
                button.click()
                time.sleep(0.3)

                image_section = image_div[0].find_elements(By.CSS_SELECTOR,
                                                           'section.slide.fluid.dkt-item.svelte-qfug6k.snap.active')

                if len(image_section) > 0:
                    image_source = image_section[0].find_elements(By.CSS_SELECTOR, 'img')

                    if len(image_source) > 0:
                        image_link = image_source[0].get_attribute('src')
                        images.append(image_link)

    return images


def check_next_image(driver):
    search_result = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Scroll down"]')
    return len(search_result) > 0


def get_next_image_button(driver):
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Scroll down"]')
    return next_button


def parse_all_reviews(driver, review_page_limit):
    reviews = []

    review_page_count = 0

    try:
        while check_next_review(driver):
            if review_page_count == review_page_limit: break

            reviews = reviews + get_reviews(driver)

            next_button = get_next_button_review(driver)
            next_button.click()

            time.sleep(1)

            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

            review_page_count += 1
    except:
        print('ERROR IN DECA REVIEW LOOP')

    return reviews


def get_reviews(driver):
    paragraph_list = driver.find_elements(By.CSS_SELECTOR, "p.answer-body.svelte-1v1nczs")

    reviews = []

    for p in paragraph_list:
        reviews.append(p.text)
        time.sleep(0.1)

    return reviews


def check_next_review(driver):
    search_result = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Next review page"]')
    return len(search_result) > 0


def get_next_button_review(driver):
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next review page"]')
    return next_button
