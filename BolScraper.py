import requests
from bs4 import BeautifulSoup


def bol_scraper(search_value, selected_category):
    # Creating object to put in scraped data
    scrape_data = {'reviews': [], 'images': []}

    # Setting link and params
    search_url = 'https://www.bol.com/nl/nl/s/'
    params = {'searchtext': search_value, 'sort': 'rating1'}

    # Search for params
    response = requests.get(search_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:

        # Parse the response with BeautifulSoup
        current_page_soup = BeautifulSoup(response.content, 'html.parser')

        # Get the list of categories
        category_list_soup = current_page_soup.find_all('div', {
            'class': 'facet-control__filter facet-control__filter--no-padding'})

        # Get the soup related to the given category
        categorized_soup = get_category_soup(category_list_soup, selected_category)

        # Get nax buttons
        pagination = categorized_soup.find('ul', {'class': 'pagination'})
        page_links = pagination.find_all('li')

        # Initializing page numbers/settings
        current_page = 1
        last_page = get_last_page_number(page_links)

        past_initial = False

        for x in range(current_page - 1, last_page - 1):
            print(x)

            # If comment out should go through every page
            if x == 1:
                break

            # Get the page soup
            if past_initial:
                categorized_soup = find_page_soup(page_links, current_page)
            else:
                past_initial = True

            # Gets the links to the products
            product_links = categorized_soup.find_all('a', {
                'class': 'product-title px_list_page_product_click list_page_product_tracking_target'})

            # Get links from products
            links = get_page_product_links(product_links)

            # Visits products link and scrape image and review data
            for link in links:
                # Send a GET request to the product page and get the response
                product_response = requests.get('https://www.bol.com' + link)

                # Parse the HTML content of the product page using BeautifulSoup
                product_soup = BeautifulSoup(product_response.content, 'html.parser')

                scrape_data['reviews'] = scrape_data['reviews'] + scrape_review_bodies(product_soup)
                scrape_data['images'] = scrape_data['images'] + scrape_image_links(product_soup)

    return scrape_data


def scrape_review_bodies(product_soup):
    # Find the product reviews
    review_container = product_soup.findAll('li', {'class': 'review js-review'})

    # Loops trough ze reviews
    return get_review_bodies(review_container)


def scrape_image_links(product_soup):
    # Find the product image
    product_image_ref = product_soup.findAll('img', {'class': 'js_selected_image has-zoom'})

    # Loops trough ze images
    return get_image_links(product_image_ref)


def get_page_product_links(product_links):
    links = []

    for link in product_links:
        # Get the URL of the product page
        product_url = link['href']

        links.append(product_url)

    return links


def get_category_soup(categories, selected_category):
    for category in categories:
        ref = category.find('a')
        cat = ref.text.split(" ")[0]

        if cat == selected_category:
            href = ref['href']
            cat_res = requests.get('https://www.bol.com' + href)

            return BeautifulSoup(cat_res.content, 'html.parser')


def get_last_page_number(page_links):
    if page_links:
        ca = page_links[len(page_links) - 2]

        if ca:
            return int(ca.text)


# messy tbh
def find_page_soup(page_links, current_page):
    for link in page_links:
        a = link.find('a')
        if a:
            a_number = a.text
            if a_number:
                if (int(a_number) > current_page) & ('js_pagination_item' in str(a)):
                    href = a['href']

                    pag_res = requests.get('https://www.bol.com' + href)

                    new_page_soup = BeautifulSoup(pag_res.content, 'html.parser')

                    pagination = new_page_soup.find('ul', {'class': 'pagination'})

                    current_page = int(a_number)
                    page_links = pagination.find_all('li')

                    return new_page_soup


def get_image_links(product_image_ref):
    images = []

    for img in product_image_ref:
        # gets src for filename
        src = img.get('src')

        if src not in images:
            images.append(src)

    return images


def get_review_bodies(review_container):
    reviews = []

    for r_data in review_container:
        r_body = r_data.find('p', {'data-test': 'review-body'})
        if r_body:
            review_text = r_body.text.strip()

            if str(review_text) not in reviews:
                # sweet spot for bol reviews seem to be around 5 -> 10
                if review_text and len(review_text.split()) > 5:
                    reviews.append(str(review_text))

    return reviews
