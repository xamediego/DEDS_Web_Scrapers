from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


async def get_ama_data(search_term):
    print('Amazon scrape')
    amazon_data = sel_scrape_amazon(search_term)

    return amazon_data


def sel_scrape_amazon(search_term):
    data = {"reviews": [], "images": []}

    driver = webdriver.Edge()

    initial_navigation(driver, search_term)

    url = driver.current_url

    r_data = prod_page(driver)

    data['reviews'] = data['reviews'] + r_data['reviews']
    data['images'] = data['images'] + r_data['images']

    # while check_next(driver, url):
    #     url = get_next_url(driver)
    #
    #     r_data = prod_page(driver)
    #
    #     data['reviews'] = data['reviews'] + r_data['reviews']
    #     data['images'] = data['images'] + r_data['images']

    return data


def initial_navigation(driver, search_term):
    driver.get("https://www.amazon.nl")

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )

    search_box.send_keys(search_term)

    search_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    search_button.click()

    category_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchDropdownBox"))
    )

    category_dropdown.send_keys("Kleding, schoenen en sieraden")

    search_box.submit()


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
    driver.get(link)

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

    driver.get(product_url)

    review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')

    try:
        for review_element in review_elements:
            review = review_element.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]')

            review_text = review.text
            print(review_text)

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
