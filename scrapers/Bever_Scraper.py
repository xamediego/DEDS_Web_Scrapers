from selenium import webdriver
from selenium.webdriver.common.by import By
import time

import Tools
from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit):
    data = scraper(search_term, page_limit)

    return data


def scraper(search_value, page_limit):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles': []}

    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, 'https://www.bever.nl/', search_value)

    url = driver.current_url
    page_counter = 0

    try:
        while (page_counter != page_limit) & (check_next(driver, url)):
            url = get_next_url(driver)

            click_consent_button(driver)

            data['titles'] = data['titles'] + get_titles(driver)

            r_data = prod_page(driver)
            data['prices'] = data['prices'] + r_data['prices']
            data['images'] = data['images'] + r_data['images']

            page_counter += 1
    except:
        print('ERROR IN BEVER PAGE LOOP')

    try:
        driver.close()
    except:
        print('Message: no such window: target window already closed')

    print('BEVER SCRAPE END')
    get_scraped_data_size_info(data)

    return data


def get_titles(driver):
    titles = []

    product_tiles = driver.find_elements(By.CSS_SELECTOR, 'div.as-t-product-grid__item')

    for product in product_tiles:
        title_span = product.find_elements(By.CSS_SELECTOR, 'span.as-a-text.as-m-product-tile__name')
        if len(title_span) > 0:
            titles.append(title_span[0].text)

    return titles


def prod_page(driver):
    data = {'reviews': [], 'images': [], 'prices': []}

    prod_content = driver.find_elements(By.CSS_SELECTOR, 'a.as-a-link.as-a-link--container.as-m-product-tile__link')

    prod_links = []

    try:
        for product in prod_content:
            try:
                prod_link = product.get_attribute('href')

                prod_links.append(prod_link)
            except:
                print('ERROR IN BEVER SCRAPER WHILE GETTING PRODUCT LINK')
    except:
        print('ERROR WHILE GETTING LINKS')

    time.sleep(1)

    try:
        for prod_link in prod_links:
            Tools.load_page(driver, prod_link, 30)

            time.sleep(1)

            new_images = get_images(driver)
            data['images'] = data['images'] + new_images

            prices = driver.find_elements(By.CSS_SELECTOR, 'span[data-qa="sell_price"]')

            if len(prices) > 0:
                price = prices[0]
                string_with_euro_symbol = price.text
                string_without_euro_symbol = string_with_euro_symbol.replace("€", "")

                data['prices'].append(string_without_euro_symbol)
    except:
        print('ERROR IN BEVER IMG LOOP')

    return data


def get_images(driver):
    images = []

    image_containers = driver.find_elements(By.CSS_SELECTOR, 'div.as-m-product-image-magnify')

    for image_container in image_containers:
        images_element = image_container.find_elements(By.CSS_SELECTOR, 'img')

        if len(images_element) > 0:
            image_link = images_element[0].get_attribute('src')

            images.append(image_link)

    return images


def initial_navigation(driver, site_url, search_value):
    Tools.load_page(driver, site_url, 30)

    time.sleep(1)

    click_consent_button(driver)

    search_bar = driver.find_element(By.CSS_SELECTOR, 'div.as-o-top-bar')

    search_box = search_bar.find_element(By.ID, 'search')

    search_box.send_keys(search_value)

    search_box.submit()


def check_next(driver, link):
    Tools.load_page(driver, link, 30)

    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'a[rel="next"]')

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')

    return search_result.get_attribute('href')


def click_consent_button(driver):
    consent_button = driver.find_elements(By.ID, 'accept-all-cookies')

    if len(consent_button) > 0:
        consent_button[0].click()
