from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit):
    data = scraper(search_term, page_limit)

    return data


def scraper(search_value, page_limit):
    data = {'reviews': [], 'images': [], 'prices': []}

    driver = webdriver.Edge()

    initial_navigation(driver, 'https://www.bever.nl/', search_value)

    url = driver.current_url
    page_counter = 0

    while (page_counter != page_limit) & (check_next(driver, url)):

        url = get_next_url(driver)

        click_consent_button(driver)

        r_data = prod_page(driver)

        data['prices'] = data['prices'] + r_data['prices']
        data['images'] = data['images'] + r_data['images']

        get_scraped_data_size_info(data)

        page_counter += 1

    return data


def prod_page(driver):
    data = {'reviews': [], 'images': [], 'prices': []}

    prod_content = driver.find_elements(By.CSS_SELECTOR, 'a.as-a-link.as-a-link--container.as-m-product-tile__link')

    print('PROD COUNT: ' + str(len(prod_content)))

    prod_links = []

    try:
        for product in prod_content:
            try:
                prod_links.append(product.get_attribute('href'))
            except:
                print('ERROR IN BEVER SCRAPER WHILE GETTING PRODUCT LINK')
    except:
        print('ERROR WHILE GETTING LINKS')

    print(len(prod_links))
    time.sleep(1)

    for prod_link in prod_links:
        driver.get(prod_link)

        time.sleep(1)

        data['images'] = data['images'] + get_images(driver)

        prices = driver.find_elements(By.CSS_SELECTOR, 'span[data-qa="sell_price"]')

        if len(prices) > 0:
            price = prices[0]
            string_with_euro_symbol = price.text
            string_without_euro_symbol = string_with_euro_symbol.replace("€", "")

            data['prices'].append(string_without_euro_symbol)

    return data


def get_images(driver):
    images = []

    image_containers = driver.find_elements(By.CSS_SELECTOR, 'div.as-m-product-image-magnify')

    for image_container in image_containers:
        images = image_container.find_elements(By.CSS_SELECTOR, 'img')

        if len(images) > 0:
            images.append(images[0].get_attribute('src'))

    return images


def initial_navigation(driver, site_url, search_value):
    driver.get(site_url)

    time.sleep(1)

    click_consent_button(driver)

    search_bar = driver.find_element(By.CSS_SELECTOR, 'div.as-o-top-bar')

    search_box = search_bar.find_element(By.ID, 'search')

    search_box.send_keys(search_value)

    search_box.submit()


def check_next(driver, link):
    driver.get(link)

    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'a[rel="next"]')

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')

    return search_result.get_attribute('href')


def click_consent_button(driver):
    consent_button = driver.find_elements(By.ID, 'accept-all-cookies')

    if len(consent_button) > 0:
        consent_button.click()
