import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


async def get_deca_data(hdr, search_term, deca_category):
    print('Deca scrape')
    deca_data = await start_scraper(hdr, search_term, deca_category)

    return deca_data


async def start_scraper(headers, search_value, selected_category):
    scrape_data = {'reviews': [], 'images': []}

    # Setting link and params
    search_url = f'https://www.decathlon.nl/search?Ntt={search_value}'
    params = {'searchtext': search_value}

    # Search for params
    response = requests.get(search_url, params=params, headers=headers, timeout=15)

    print(response.status_code)

    if response.status_code == 200:
        scrape_data = await scraper(response)

    return scrape_data


async def scraper(response):
    scrape_data = {'reviews': [], 'images': []}

    driver = webdriver.Edge()

    # Parse the response with BeautifulSoup
    current_page_soup = BeautifulSoup(response.content, 'html.parser')

    div_element = current_page_soup.find_all('div', {
        'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

    for prod_div in div_element:
        link = prod_div.find('a')

        product_link = link['href']

        link = f"https://www.decathlon.nl/{product_link}"
        new_link = link.replace("nl//p/", "nl/r/")

        driver.get(new_link)

        agree_cookie_consent(driver)

        # scrape_data['reviews'] = scrape_data['reviews'] + await get_reviews(driver)
        scrape_data['reviews'] = scrape_data['reviews'] + await parse_all_reviews(driver)

        print('CURRENT COMPLETE R COUNT: ' + str(len(scrape_data['reviews'])))

    return scrape_data


def agree_cookie_consent(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")

    for button in buttons:
        if button.text == 'Akkoord en sluiten':
            button.click()
            break


def get_current_nav_number(driver):
    current_page_number = 0

    current_page_span = driver.find_elements(By.CSS_SELECTOR, "span.current-page svelte-193vb4x")
    if current_page_span:
        current_page_number = int(current_page_span[0].text)

    return current_page_number


def get_last_nav_number(driver):
    nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

    last_page_number = 1

    if nav_buttons:
        ind = len(nav_buttons) - 2
        last_page_number = nav_buttons[ind].text

    return last_page_number


async def parse_all_reviews(driver):
    reviews = []

    current_page_number = get_current_nav_number(driver)
    last_page_number = get_last_nav_number(driver)

    nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

    print(f"CURRENT: {current_page_number} | LAST: {last_page_number}")

    try:
        while int(current_page_number) < int(last_page_number):

            print('GET R')
            reviews = reviews + await get_reviews(driver)

            print("REVIEW COUNT: " + str(len(reviews)))

            await navigate_reviews(nav_buttons, current_page_number)

            current_page_number += 1

            nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

            last_page_number = int(nav_buttons[len(nav_buttons) - 2].text)

            print(f"CURRENT: {current_page_number} | LAST: {last_page_number}")
    except:
        print('ERROR WHILE NAVIGATING REVIEWS')

    return reviews


async def navigate_reviews(nav_buttons, current_page_number):
    for button in nav_buttons:
        try:
            if button.text:
                v = button.text

                if int(v) > (current_page_number + 1):
                    print('NEW PAGE: ' + v)
                    button.click()
                    break
        except:
            print('ERROR WHEN NAVIGATING')


async def get_reviews(driver):
    paragraph_list = driver.find_elements(By.CSS_SELECTOR, "p.answer-body.svelte-1v1nczs")

    reviews = []

    for p in paragraph_list:
        try:
            reviews.append(p.text)
        except:
            print('ERROR WHEN GETTING REVIEW')

    print('ADD: R ' + str(len(reviews)))

    return reviews
