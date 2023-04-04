import requests
from bs4 import BeautifulSoup


def start_scraper(search_value, selected_category):
    scrape_data = {'reviews': [], 'images': []}

    # Setting link and params
    search_url = 'https://www.amazon.com/'
    params = {'searchtext': search_value}

    # Search for params
    response = requests.get(search_url)

    print(response.status_code)

    if response.status_code == 200:
        scrape_data = scraper(response)

    return scrape_data


def scraper(response):
    scrape_data = {'reviews': [], 'images': []}

    print('RESPONSE 200')

    # Parse the response with BeautifulSoup
    current_page_soup = BeautifulSoup(response.content, 'html.parser')

    # print(current_page_soup)
    # print('---------------')

    pagination = current_page_soup.find_all('div', {
        'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

    for prod_div in pagination:
        print(prod_div)

    return scrape_data
