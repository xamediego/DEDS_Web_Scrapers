import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def start_scraper(headers, search_value, selected_category):
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
        scrape_data = scraper(response, headers)

    return scrape_data


def scraper(response, headers):
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

        while int(current_page_number) < int(last_page_number):
            nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")

            paras = driver.find_elements(By.CSS_SELECTOR, "p.answer-body.svelte-1v1nczs")

            for pa in paras:
                try:
                    print('ADDED REVIEW: ' + pa.text)
                    scrape_data['reviews'].append(pa.text)
                except:
                    print('ERROR WHILE FINDING TEXT')

            print("REVIEW COUNT: " + str(len(scrape_data['reviews'])))

            print(len(nav_buttons) - 2)

            for x in range(0, len(nav_buttons) - 2):
                print(nav_buttons[x])
                b_t = nav_buttons[x].text
                print('B_T: ' + b_t + ' > ' + str(current_page_number))

                button_classname = nav_buttons[x].get_attribute("class")
                print(f"Button classname: {button_classname}")

                if b_t:
                    if int(b_t) > int(current_page_number + 1):
                        nav_buttons[x].click()
                        break

            current_page_number += 1

            nav_buttons = driver.find_elements(By.CSS_SELECTOR, "button.svelte-193vb4x")
            last_page_number = int(nav_buttons[len(nav_buttons) - 2].text)

            print(f"CURRENT: {current_page_number} | LAST: {last_page_number}")

    return scrape_data
