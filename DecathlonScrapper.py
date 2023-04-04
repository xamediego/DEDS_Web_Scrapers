import requests
from bs4 import BeautifulSoup


def scraper(search_value, selected_category):
    scrape_data = {'reviews': [], 'images': []}

    # Setting link and params
    search_url = 'https://www.decathlon.nl/'

    params = {'searchtext': search_value}

    # Search for params
    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        print('RESPONSE 200')

        # Parse the response with BeautifulSoup
        current_page_soup = BeautifulSoup(response.content, 'html.parser')

        # print(current_page_soup)
        # print('---------------')

        pagination = current_page_soup.find_all('div', {'class': 'product-block-top-main vtmn-flex vtmn-flex-col vtmn-items-center'})

        print(pagination)

        for prod_div in pagination:

    return scrape_data
