import os
import requests
from bs4 import BeautifulSoup
import re

cat = ['jassen']
selected_category = 'Herenmode'

search_url = 'https://www.bol.com/nl/nl/s/'
params = {'searchtext': cat[0], 'sort': 'rating1'}

response = requests.get(search_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    print('RES 200')
    # Parse the response with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    categories2 = soup.find_all('div', {'class': 'facet-control__filter facet-control__filter--no-padding'})

    for category in categories2:
        ref = category.find('a')
        cat = ref.text.split(" ")[0]

        if cat == selected_category:
            href = ref['href']
            print('https://www.bol.com' + href)
            cat_res = requests.get('https://www.bol.com' + href)

            soup = BeautifulSoup(cat_res.content, 'html.parser')

    current_page = 1
    past_initial = False

    pagination = soup.find('ul', {'class': 'pagination'})
    page_links = pagination.find_all('li')
    print(len(page_links))

    ca = page_links[len(page_links) - 1].find('a')

    if ca:
        print(ca)
        print(ca.text)


    for link in page_links:
        span = link.find('span')

        if span:
            print('CURRENT: ' + str(current_page))
            current_page = span.text

        a = link.find('a')

        if a:
            a_number = a.text
            pattern = '[0-9]*'

            if past_initial & (a_number > current_page) & ('js_pagination_item' in str(a)) & (a_number != current_page):
                print('NEW: ' + str(a_number))

                current_page = a_number
                href = a['href']

                pag_res = requests.get('https://www.bol.com' + href)

                soup = BeautifulSoup(pag_res.content, 'html.parser')

                pagination = soup.find('ul', {'class': 'pagination'})
                page_links = pagination.find_all('li')
                break
        past_initial = True


    # Gets the links to the products
    product_links = soup.find_all('a', {
        'class': 'product-title px_list_page_product_click list_page_product_tracking_target'})

    print(product_links)

    links = []

    for link in product_links:
        # Get the URL of the product page
        product_url = link['href']

        links.append(product_url)

    for link in links:
        # Send a GET request to the product page and get the response
        product_response = requests.get('https://www.bol.com' + link)

        # Parse the HTML content of the product page using BeautifulSoup
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Find the product image
        product_image_ref = product_soup.findAll('img', {'class': 'js_selected_image has-zoom'})
        images = []

        # Loops trough ze images
        for img in product_image_ref:
            # gets src for filename
            src = img.get('src')

            if src not in images:
                images.append(src)

            # # gets the image from the bol
            # response = requests.get(src)
            #
            # # creates the filename and filepath (stores it to the project root / images
            # filename = os.path.basename(src)
            #
            # filepath = os.path.join("images", str(filename))
            #
            # # writes the image to the folder
            # with open(filepath, "wb") as f:
            #     f.write(response.content)

        # Find the product reviews
        review_container = product_soup.findAll('li', {'class': 'review js-review'})

        reviews = []

        # Loops trough ze reviews
        for r_data in review_container:
            r_body = r_data.find('p', {'data-test': 'review-body'})
            if r_body:
                review_text = r_body.text.strip()

                if str(review_text) not in reviews:
                    reviews.append(str(review_text))
