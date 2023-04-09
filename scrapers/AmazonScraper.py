from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

import Tools
from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit, review_page_limit):
    amazon_data = sel_scrape_amazon(search_term, page_limit, review_page_limit)

    return amazon_data


def sel_scrape_amazon(search_term, page_limit, review_page_limit):
    data = {"reviews": [], "images": [], 'prices': [], 'titles': []}

    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, search_term, "https://www.amazon.nl")

    url = driver.current_url
    page_counter = 0

    while (page_counter != page_limit) & (check_next(driver, url)):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

        url = get_next_url(driver)

        data['prices'] = data['prices'] + get_prices(driver)
        data['titles'] = data['titles'] + get_titles(driver)

        r_data = prod_page(driver, review_page_limit)
        print('PRD')
        print(r_data['reviews'])
        print(r_data['images'])
        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']
        print('PRD 2')
        print(data['reviews'])
        print(data['images'])

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


def prod_page(driver, review_page_limit):
    search_results = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')

    soup_result = []

    for result in search_results:
        html = result.get_attribute('innerHTML')
        soup_result.append(BeautifulSoup(html, 'html.parser'))

    return parse_page(driver, soup_result, review_page_limit)


def parse_page(driver, soup_result, review_page_limit):
    data = {"reviews": [], "images": []}

    for result in soup_result:
        a_tag = result.select_one('a.a-link-normal.s-no-outline')

        p_link = 'https://www.amazon.nl' + a_tag['href']

        r_data = get_data(driver, p_link, review_page_limit)
        print('R_DATA REVIEWS')
        print(r_data['reviews'])

        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']

    print('DATA')
    print(data['reviews'])
    print(data['images'])
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


def get_data(driver, product_url, review_page_limit):
    images = []

    Tools.load_page(driver, product_url, 30)

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    image_elements = driver.find_elements(By.CSS_SELECTOR, 'img.a-dynamic-image')


    for image_element in image_elements:
        images.append(image_element.get_attribute("src"))


    reviews = get_all_reviews(driver, review_page_limit)

    return {"reviews": reviews, "images": images}


def get_all_reviews(driver, review_page_limit):
    reviews = []

    more_reviews_link = driver.find_elements(By.CSS_SELECTOR, 'a[data-hook="see-all-reviews-link-foot"]')

    if len(more_reviews_link) > 0:
        more_reviews_link[0].click()

        try_translate(driver)
        page_count = 0

        while (page_count == review_page_limit) & (check_review_next(driver)):

            try_translate(driver)

            review_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-hook="review-body"]')

            for review in review_elements:
                review_text = review.text

                print(review_text)

                reviews.append(review_text)

            next_link = get_next_review_link(driver)
            next_link.click()
            time.sleep(8)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

            page_count += 1

    print('GOT REVIEWS')
    print(reviews)

    return reviews


def try_translate(driver):
    translate_link_a = driver.find_elements(By.CSS_SELECTOR, 'a[data-hook="cr-translate-these-reviews-link"]')
    if len(translate_link_a) > 0:
        try:
            translate_link_a[0].click()
            time.sleep(15)
        except:
            print('ERROR WHILE PRESSING TRANSLATE BUTTON')


def check_review_next(driver):
    pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.a-pagination')

    if len(pagination) > 0:
        next_line_button = pagination[0].find_elements(By.CSS_SELECTOR, 'li.a-last')

        next_line_link = next_line_button[0].find_elements(By.CSS_SELECTOR, 'a')

        return len(next_line_link) > 0

    return False


def get_next_review_link(driver):
    pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.a-pagination')

    if len(pagination) > 0:
        next_line_button = pagination[0].find_elements(By.CSS_SELECTOR, 'li.a-last')

        next_line_link = next_line_button[0].find_elements(By.CSS_SELECTOR, 'a')

        return next_line_link[0]
