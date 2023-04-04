import requests
from bs4 import BeautifulSoup


def scrape_adidas(headers, search_term):
    print('start scrape')

    # Set the URL for Adidas.nl with the search term
    url = f"https://www.adidas.nl/search?q={search_term}"

    print(url)

    print('SEND GET')
    # Send a request to the URL and get the response
    response = requests.get(url, headers=headers, timeout=30)

    print(response.status_code)

    # Parse the response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # print(soup)
    a = soup.find("div", {"class": "sheet___2Zvfp page-content___2Bh3s"})

    b = a.find_all("a")

    for links in b:
        print('------------')
        print(links)

    # Extract the relevant information from each product item
    reviews = []
    images = []

    data = {"reviews": reviews, "images": images}

    return data
