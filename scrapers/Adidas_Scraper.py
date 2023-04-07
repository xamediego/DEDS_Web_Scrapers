import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def scrape_full(search_term):
    adidas_data = scraper(search_term)

    return adidas_data


def initial_navigation(driver, site_url, search_term):
    url = site_url + search_term

    driver.get(url)

    click_consent_button(driver)


def click_consent_button(driver):
    consent_button = driver.find_element(By.ID, 'glass-gdpr-default-consent-accept-button')

    consent_button.click()


def scraper(search_term):
    data = {'reviews': [], 'images': []}

    driver = webdriver.Edge()

    initial_navigation(driver, 'https://www.adidas.nl/search?q=', search_term)

    # Adidas site is bloated
    time.sleep(5)

    url = driver.current_url

    while check_next(driver, url):
        close_account_portal(driver)

        url = get_next_url(driver)

        r_data = prod_page(driver)

        data['reviews'] = data['reviews'] + r_data['reviews']
        data['images'] = data['images'] + r_data['images']

    return data


def prod_page(driver):
    data = {'reviews': [], 'images': []}

    product_content = driver.find_element(By.CSS_SELECTOR, 'div.plp-grid___1FP1J')

    product_links = product_content.find_elements(By.CSS_SELECTOR, 'a.glass-product-card__assets-link')

    product_href = []

    for link in product_links:
        url = link.get_attribute('href')
        product_href.append(url)

    for link in product_href:
        driver.get(link)

        time.sleep(2)

        close_account_portal(driver)

        time.sleep(0.5)

        open_review_div = driver.find_element(By.ID, 'navigation-target-reviews')
        open_review_button = open_review_div.find_elements(By.CSS_SELECTOR, 'button.accordion__header___3Pii5')

        data['images'] = data['images'] + get_images(driver)

        for r_b in open_review_button:
            r_b.click()

        open_lees_meer(driver)

        review_articles = driver.find_elements(By.CSS_SELECTOR, 'article.review___3M74F.gl-vspace-bpall-medium')

        for review_article in review_articles:
            try:
                data['reviews'].append(parse_review(review_article))
            except:
                print('ERROR WHILE RETRIEVING REVIEW')

        return data


def check_next(driver, link):
    driver.get(link)

    time.sleep(5)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'a[data-auto-id="plp-pagination-next"]')

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR, 'a[data-auto-id="plp-pagination-next"]')

    return search_result.get_attribute('href')


def get_images(driver):
    images_div = driver.find_element(By.ID, 'pdp-gallery-desktop-grid-container')
    images_holder = images_div.find_elements(By.CSS_SELECTOR, 'img')

    images = []

    for x in range(0, 4):
        images.append(images_holder[x].get_attribute('src'))

    print(images)

    return images


def parse_review(review_article):
    try:
        read_more = review_article.find_element(By.CSS_SELECTOR, 'button[data-auto-id="review-read-more-button"]')
        read_more.click()

        time.sleep(0.2)

        translate_div = review_article.find_elements(By.CSS_SELECTOR, 'div.translation-info___1r8vO')
        if len(translate_div) > 0:
            for t_d in translate_div:
                t_d.click()

        time.sleep(0.2)

        review_text_div = review_article.find_element(By.CSS_SELECTOR,
                                                      'div.clamped____ERX6.gl-vspace.gl-body.gl-no-margin-bottom.expanded___1g3ZG')
        review_text = review_text_div.text
        return review_text
    except:
        print('ERROR WHILE PARSING REVIEW')


def open_lees_meer(driver):
    reviews_div = driver.find_element(By.CSS_SELECTOR, 'div.reviews___3fzxE')
    lees_meer_button = reviews_div.find_elements(By.CSS_SELECTOR, 'button[data-auto-id="ratings-load-more"]')

    if len(lees_meer_button) > 0:
        for l_m_b in lees_meer_button:
            l_m_b.click()

            time.sleep(0.3)

            open_lees_meer(driver)

            break


def close_account_portal(driver):
    account_portal_button = driver.find_elements(By.NAME, 'account-portal-close')

    for b in account_portal_button:
        b.click()
