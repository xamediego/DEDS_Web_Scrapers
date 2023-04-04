import requests
from bs4 import BeautifulSoup
import re

from langdetect import detect


def scrape_amazon(headers, search_term):
    # Set the URL for Amazon.nl with the search term
    url = f"https://www.amazon.nl/s?k={search_term}"

    # Send a request to the URL and get the response
    response = requests.get(url, headers=headers)

    # Parse the response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the search result items on the page
    search_results = soup.find_all("div", {"data-component-type": "s-search-result"})

    # Extract the relevant information from each search result item
    reviews = []
    images = []

    for result in search_results:
        # Extract the product URL
        product_url = result.find("a", {"class": "a-link-normal"})["href"]
        product_url = "https://www.amazon.nl" + product_url

        # Send a request to the product URL and get the response
        response = requests.get(product_url, headers=headers)

        # Parse the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Check if the product has at least one review
        review_elements = soup.find_all("div", {"data-hook": "review"})
        if len(review_elements) == 0:
            continue

        for review_element in review_elements:
            review_text = review_element.find("span", {"data-hook": "review-body"}).text.strip()
            # Check if the review is written in Dutch using a regular expression

            if detect(review_text) == 'nl':
                reviews.append(review_text)

        # Extract the product image links
        image_elements = soup.find_all("img", {"class": "a-dynamic-image"})
        for image_element in image_elements:
            images.append(image_element["src"])


    # Create the data object with the reviews and image links
    data = {"reviews": reviews, "images": images}

    return data
