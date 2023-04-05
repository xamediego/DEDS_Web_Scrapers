import requests
from bs4 import BeautifulSoup


def scrape_adidas(headers, search_term):
    print('start scrape')

    # Set the URL for Adidas.nl with the search term
    url = f"https://www.adidas.nl/search?q={search_term}"
    url2 = 'https://www.adidas.nl/search?q=jassen'

    response = requests.get(url2, headers=headers, timeout=30)

    print(response.status_code)

    # Parse the response using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    a = soup.find_all("div", {"class": "sheet___2Zvfp page-content___2Bh3s"})

    print(a)

    for links in a:
        print('------------')
        print(links)

    # Extract the relevant information from each product item
    reviews = []
    images = []

    data = {"reviews": reviews, "images": images}

    return data
