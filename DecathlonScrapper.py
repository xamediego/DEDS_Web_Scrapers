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

    print('SEARCH AT LINK')
    print(search_url)

    # Search for params
    response = requests.get(search_url, params=params, headers=headers, timeout=15)

    print(response.status_code)

    if response.status_code == 200:
        scrape_data = await scraper(response)

    return scrape_data


# Have to use try and except because throws some error that idk how to fix

async def scraper(response):
    scrape_data = {'reviews': [], 'images': []}

    driver = webdriver.Edge()  # or webdriver.Firefox(), webdriver.Edge(), etc.

    # Parse the response with BeautifulSoup
    current_page_soup = BeautifulSoup(response.content, 'html.parser')

    div_element = current_page_soup.find_all('div', {
        'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

    for prod_div in div_element:
        link = prod_div.find('a')

        product_link = link['href']

        link = f"https://www.decathlon.nl/{product_link}"
        new_link = link.replace("nl//p/", "nl/r/")
        print(new_link)

        driver.get(new_link)

        buttons = driver.find_elements(By.TAG_NAME, "button")

        for button in buttons:
            if button.text == 'Akkoord en sluiten':
                button.click()
                break

        current_page_number = 0
        last_page_number = 1

        current_page_span = driver.find_elements(By.CSS_SELECTOR, "span.current-page svelte-193vb4x")
        if current_page_span:
            print('CURRENT PAGE SPAN: ' + str(current_page_span))
            current_page_number = int(current_page_span[0].text)

        nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")
        if nav_buttons:
            ind = len(nav_buttons) - 2
            print('LAST: ' + nav_buttons[ind].text)
            last_page_number = nav_buttons[ind].text

        print(f"CURRENT: {current_page_number} | LAST: {last_page_number}")

        try:
            while int(current_page_number) < int(last_page_number):
                nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

                paras = driver.find_elements(By.CSS_SELECTOR, "p.answer-body.svelte-1v1nczs")

                scrape_data['reviews'] = scrape_data['reviews'] + await get_reviews(paras)

                print("REVIEW COUNT: " + str(len(scrape_data['reviews'])))

                await navigate_reviews(nav_buttons, current_page_number)

                current_page_number += 1

                nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

                last_page_number = int(nav_buttons[len(nav_buttons) - 2].text)

                print(f"CURRENT: {current_page_number} | LAST: {last_page_number}")
        except:
            print('ERROR WHEN PARSING')

    return scrape_data


async def navigate_reviews(nav_buttons, current_page_number):
    for button in nav_buttons:
        try:
            if button.text:
                print(button.text + ' > ' + str((current_page_number + 1)))
                v = button.text

                if int(v) > (current_page_number + 1):
                    print('NEW PAGE: ' + v)
                    button.click()
                    break
        except:
            print('ERROR WHEN NAVIGATING')


async def get_reviews(paragraph_list):
    reviews = []

    for pa in paragraph_list:
        try:
            print('REVIEW: ' + pa.text)
            reviews.append(pa.text)
        except:
            print('ERROR WHEN GETTING REVIEW')

    return reviews
