import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def scrape_full(search_term):
    print('Deca scrape')
    deca_data = start_scraper(search_term)

    return deca_data


def start_scraper(search_value):
    data = {'reviews': [], 'images': []}

    driver = webdriver.Edge()

    initial_navigation(driver, 'https://www.decathlon.nl/', search_value)

    url = driver.current_url

    while check_next(driver, url):
        next_button = get_next_button(driver)

        product_list = driver.find_element(By.CSS_SELECTOR, "div.product-list.pl-list.js-first.svelte-1wkvbov")

        html = product_list.get_attribute('innerHTML')

        product_soup = BeautifulSoup(html, 'html.parser')

        r_data = product_loop(driver, product_soup)

        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']

        driver.get(url)

        next_button.click()
        time.sleep(4)

        url = driver.current_url

    return data


def initial_navigation(driver, site_url, search_value):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    site_url = site_url + f'search?Ntt={search_value}'

    response = requests.get(site_url, headers=hdr, timeout=15)

    driver.get(response.url)

    click_consent_button(driver)


def check_next(driver, link):
    driver.get(link)

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


def product_loop(driver, current_page_soup):
    scrape_data = {'reviews': [], 'images': []}

    div_element = current_page_soup.find_all('div', {
        'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

    for prod_div in div_element:
        scrape_data['reviews'] = scrape_data['reviews'] + p_s(driver, prod_div)

    return scrape_data


def p_s(driver, prod_soup):
    link = prod_soup.find('a')

    product_link = link['href']

    link = f"https://www.decathlon.nl/{product_link}"
    new_link = link.replace("nl//p/", "nl/r/")

    driver.get(new_link)

    reviews = parse_all_reviews(driver)

    return reviews


def parse_all_reviews(driver):
    reviews = []

    while check_next_review(driver):
        next_button = get_next_button_review(driver)

        reviews = reviews + get_reviews(driver)

        next_button.click()

        time.sleep(0.01)

    return reviews


def get_reviews(driver):
    paragraph_list = driver.find_elements(By.CSS_SELECTOR, "p.answer-body.svelte-1v1nczs")

    reviews = []

    for p in paragraph_list:
        reviews.append(p.text)

    return reviews


def check_next_review(driver):
    search_result = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Next review page"]')
    return len(search_result) > 0


def get_next_button_review(driver):
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next review page"]')
    return next_button
