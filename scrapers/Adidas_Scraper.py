import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import Tools
from Tools import get_scraped_data_size_info


def scrape_full(search_term, page_limit):
    adidas_data = scraper(search_term, page_limit)

    return adidas_data


def initial_navigation(driver, site_url, search_term):
    url = site_url + search_term

    Tools.load_page(driver, url, 40)

    time.sleep(1)

    click_consent_button(driver)


def click_consent_button(driver):
    consent_button = driver.find_element(By.ID, 'glass-gdpr-default-consent-accept-button')

    consent_button.click()


def scraper(search_term, page_limit):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles': []}

    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, 'https://www.adidas.nl/search?q=', search_term)

    # Adidas site is bloated and broken
    time.sleep(5)

    url = driver.current_url
    page_counter = 0

    try:
        while (page_counter != page_limit) & (check_next(driver, url)):
            close_account_portal(driver)

            url = get_next_url(driver)

            data['prices'] = data['prices'] + get_prices(driver)
            data['titles'] = data['titles'] + get_titles(driver)

            r_data = prod_page(driver)
            data['reviews'] = data['reviews'] + r_data['reviews']
            data['images'] = data['images'] + r_data['images']

            page_counter += 1
    except:
        print('ERROR IN ADIDAS PAGE LOOP')

    driver.close()

    print('ADIDAS SCRAPE END')
    get_scraped_data_size_info(data)

    return data


def prod_page(driver):
    data = {'reviews': [], 'images': []}

    product_content = driver.find_elements(By.CSS_SELECTOR, 'div.plp-grid___1FP1J')

    if len(product_content) > 0:
        try:
            product_links = product_content[0].find_elements(By.CSS_SELECTOR, 'a.glass-product-card__assets-link')

            product_href = []

            for link in product_links:
                url = link.get_attribute('href')
                product_href.append(url)

            for link in product_href:
                Tools.load_page(driver, link, 40)

                time.sleep(2)

                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

                close_account_portal(driver)

                time.sleep(0.5)

                open_review_div = driver.find_elements(By.ID, 'navigation-target-reviews')

                if len(open_review_div) > 0:
                    open_review_button = open_review_div[0].find_elements(By.CSS_SELECTOR,
                                                                          'button.accordion__header___3Pii5')

                    data['images'] = data['images'] + get_images(driver)

                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)

                    try:
                        for r_b in open_review_button:
                            try:
                                r_b.click()
                                print('MORE R BUTTON CLICKED')
                                time.sleep(0.5)
                            except:
                                print('ERROR IN AD SCR WHILE CLICK open review button')
                    except:
                        print('ERROR IN AD IN RWB LOOP')

                    open_lees_meer(driver)

                    time.sleep(0.2)
                    review_articles = get_articles(driver)
                    print('AMOUNT OF R ARTICLES: ' + str(len(review_articles)))
                    time.sleep(0.2)

                    for review_article in review_articles:
                        expected_review = parse_review(review_article)

                        if expected_review:
                            data['reviews'].append(expected_review)
        except:
            print('ERROR IN ADIDAS PRODUCT PAGE LOOP')

        print('R leng: ' + str(len(data['reviews'])))
        return data


def get_articles(driver):
    return driver.find_elements(By.CSS_SELECTOR,
                                           'article.review___3M74F.gl-vspace-bpall-medium')


def get_prices(driver):
    prices = []

    span_prices = driver.find_elements(By.CSS_SELECTOR, 'div.gl-price-item.notranslate')

    for price in span_prices:
        cleaned_price = price.text.replace("€", "")
        cleaned_price = cleaned_price.replace(" ", "")

        prices.append(cleaned_price)

    return prices


def get_titles(driver):
    titles = []

    product_tiles = driver.find_elements(By.CSS_SELECTOR, 'div.glass-product-card-container')

    for product in product_tiles:
        title_span = product.find_elements(By.CSS_SELECTOR, 'p.glass-product-card__title')

        if len(title_span) > 0:
            titles.append(title_span[0].text)

    return titles


def check_next(driver, link):
    Tools.load_page(driver, link, 30)

    time.sleep(5)

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    search_result = driver.find_elements(By.CSS_SELECTOR, 'a[data-auto-id="plp-pagination-next"]')

    return len(search_result) > 0


def get_next_url(driver):
    search_result = driver.find_element(By.CSS_SELECTOR, 'a[data-auto-id="plp-pagination-next"]')

    return search_result.get_attribute('href')


def get_images(driver):
    gallery_container = driver.find_elements(By.ID, 'navigation-target-gallery')

    images = []

    if len(gallery_container) > 0:
        images_div = gallery_container[0].find_elements(By.ID, 'pdp-gallery-desktop-grid-container')
        more_img_button = gallery_container[0].find_elements(By.CSS_SELECTOR,
                                                             'button[data-auto-id="image-grid-expand-button"]')

        if len(more_img_button) > 0:
            more_img_button[0].click()

        if len(images_div) > 0:
            images_holder = images_div[0].find_elements(By.CSS_SELECTOR, 'img')

            for image in images_holder:
                img_link = image.get_attribute('src')
                if img_link:
                    images.append(img_link)

    return images


def parse_review(review_article):
    read_more = review_article.find_elements(By.CSS_SELECTOR, 'button[data-auto-id="review-read-more-button"]')

    if len(read_more) > 0:
        try:
            read_more[0].click()
            time.sleep(0.1)
        except:
            print('READ MORE CLICK ERROR')

    time.sleep(0.2)

    translate_div = review_article.find_elements(By.CSS_SELECTOR, 'div.translation-info___1r8vO')
    if len(translate_div) > 0:
        for t_d in translate_div:
            try:
                t_d.click()
            except:
                print('TRANSLATE CLICK ERROR')


    time.sleep(0.2)

    review_text_div = review_article.find_elements(By.CSS_SELECTOR,
                                                   'div.clamped____ERX6.gl-vspace.gl-body.gl-no-margin-bottom.expanded___1g3ZG')

    if len(review_text_div) > 0:
        review_text = review_text_div[0].text

        return review_text


def open_lees_meer(driver):
    reviews_div = driver.find_elements(By.CSS_SELECTOR, 'div.reviews___3fzxE')

    if len(reviews_div) > 0:
        lees_meer_button = reviews_div[0].find_elements(By.CSS_SELECTOR, 'button[data-auto-id="ratings-load-more"]')

        if len(lees_meer_button) > 0:
            l_m_b = lees_meer_button[0]

            try:
                time.sleep(0.2)
                old_art_count = len(get_articles(driver))

                l_m_b.click()
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

                new_art_count = len(get_articles(driver))
                print('OLD: ' + str(old_art_count) + " | NEW: " + str(new_art_count))

                if new_art_count > old_art_count:
                    open_lees_meer(driver)
            except:
                print('LMB Message: element not interactable')


def close_account_portal(driver):
    account_portal_button = driver.find_elements(By.NAME, 'account-portal-close')

    if len(account_portal_button) > 0:
        account_portal_button[0].click()
