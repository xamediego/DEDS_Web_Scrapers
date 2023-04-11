import time

import requests
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

import Tools


def scrape_full(search_term, zalando_category, page_limit):
    print('Zalando scrape')
    zalando_data = start_scraper(search_term, zalando_category, page_limit)

    return zalando_data


def initial_navigation(driver, site_url, search_value, zalando_category):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    site_url = f'{site_url}{zalando_category}/?q={search_value}'

    response = requests.get(site_url, headers=hdr, timeout=15)

    Tools.load_page(driver, response.url, 30)

    time.sleep(1)

    click_consent_button(driver)


def start_scraper(search_value, zalando_category, page_limit):
    driver = webdriver.Edge()
    driver.set_window_size(1600, 1000)

    initial_navigation(driver, 'https://www.zalando.nl/', search_value, zalando_category)

    return product_page_catalog_loop(driver, page_limit)


def click_consent_button(driver):
    expected_consent_button = driver.find_elements(By.ID, 'uc-btn-accept-banner')

    if len(expected_consent_button) > 0:
        try:
            expected_consent_button[0].click()
        except:
            print('ERROR WHILE TRYING TO CLICK ZALANDO CONSENT BUTTON')


def product_page_catalog_loop(driver, page_limit):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles': []}

    page_counter = 0
    url = driver.current_url

    while (page_counter != page_limit) & (check_next(driver)):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)

        # Get review/images from item page
        product_data = get_data(driver)

        if product_data:
            data['reviews'] = data['reviews'] + product_data['reviews']
            data['images'] = data['images'] + product_data['images']
            data['prices'] = data['prices'] + product_data['prices']
            data['titles'] = data['titles'] + product_data['titles']

        # Navigate to next page
        Tools.load_page(driver, url, 30)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

        click_consent_button(driver)
        next_button = get_next_button(driver)
        time.sleep(1)
        next_button.click()
        time.sleep(4)

        page_counter += 1

        url = driver.current_url

    try:
        driver.close()
    except:
        print('Message: no such window: target window already closed')

    print('ZALANDO SCRAPE END')
    Tools.get_scraped_data_size_info(data)

    return data


def check_next(driver):
    navigation_bar = driver.find_elements(By.CSS_SELECTOR, 'nav.VKvyEj._0xLoFW._7ckuOK.mROyo1.uEg2FS')
    print(len(navigation_bar))

    if len(navigation_bar) > 0:
        next_page_ref = navigation_bar[0].find_elements(By.CSS_SELECTOR, 'a[title="Volgende pagina"]')
        if len(next_page_ref) > 0:
            next_page_link = next_page_ref[0].get_attribute('href')
            return next_page_link is not None

    return False


def get_next_button(driver):
    navigation_bar = driver.find_elements(By.CSS_SELECTOR, 'nav.VKvyEj._0xLoFW._7ckuOK.mROyo1.uEg2FS')
    next_page_ref = navigation_bar[0].find_elements(By.CSS_SELECTOR, 'a[title="Volgende pagina"]')

    return next_page_ref[0]


def get_data(driver):
    data = {'reviews': [], 'images': [], 'prices': [], 'titles': []}

    product_content = driver.find_elements(By.CSS_SELECTOR, 'article._0mW-4D._0xLoFW.JT3_zV.mo6ZnF._78xIQ-')

    product_page_links = []

    for product in product_content:

        price = product.find_elements(By.CSS_SELECTOR, 'p._0Qm8W1.u-6V88.dgII7d.TQ5FLB')
        if len(price) > 0:
            data['prices'].append(price[0].text)

        title = product.find_elements(By.CSS_SELECTOR,
                                      'h3._0Qm8W1.u-6V88.FxZV-M.pVrzNP.ZkIJC-.r9BRio.qXofat.EKabf7.nBq1-s._2MyPg2')
        if len(title) > 0:
            data['titles'].append(title[0].text)

        a_link = product.find_elements(By.CSS_SELECTOR, 'a._LM.JT3_zV.CKDt_l.CKDt_l.LyRfpJ')
        if len(a_link) > 0:
            product_page_links.append(a_link[0].get_attribute('href'))

    for link in product_page_links:
        prod_data = get_product_data(driver, link)
        time.sleep(1)

        data['reviews'] = data['reviews'] + prod_data['reviews']
        data['images'] = data['images'] + prod_data['images']

        time.sleep(1)

    return data


def get_product_data(driver, link):
    driver.get(link)
    time.sleep(1)

    data = {'images': get_images(driver), 'reviews': get_reviews(driver)}

    return data


def get_reviews(driver):
    reviews = []

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    expected_review_button = driver.find_elements(By.ID, 'z-pdp-all-reviews')

    if len(expected_review_button) > 0:
        expected_review_button[0].click()
        time.sleep(2)

        review_container = driver.find_elements(By.CSS_SELECTOR, 'div[aria-labelledby="pdp_reviews-dialog_title"]')

        if len(review_container) > 0:

            press_load_more(review_container[0])
            time.sleep(0.5)

            expected_reviews_list = review_container[0].find_elements(By.CSS_SELECTOR, 'ul.DT5BTM._2hG8pA._4oK5GO')

            if len(expected_reviews_list) > 0:
                expected_reviews_list_items = expected_reviews_list[0].find_elements(By.CSS_SELECTOR, 'li')

                for item in expected_reviews_list_items:
                    review = item.find_elements(By.CSS_SELECTOR, 'p._0Qm8W1.u-6V88.FxZV-M.pVrzNP.f4ql6o')
                    if len(review) > 0:
                        review_text = review[0].text
                        reviews.append(review_text)

    return reviews


def press_load_more(review_container):
    expected_load_more_button = review_container.find_elements(By.XPATH, "//*[contains(text(), 'Meer laden')]")

    if len(expected_load_more_button) > 0:
        expected_load_more_button[0].click()
        press_load_more(review_container)


def get_images(driver):
    images = []

    image_list = driver.find_elements(By.CSS_SELECTOR, 'ul[aria-label="Productmediagalerij"]')

    if (len(image_list)) > 0:
        items = image_list[0].find_elements(By.CSS_SELECTOR, 'li')
        l_counter = 1

        for item in items:

            if l_counter % 5 == 0:
                img_scroll_down(driver)

            try:
                img_button = item.find_element(By.CSS_SELECTOR, 'button')
                img_button.click()
            except:
                try:
                    img_scroll_down(driver)

                    img_button = item.find_element(By.CSS_SELECTOR, 'button')
                    img_button.click()
                except:
                    print('TRIED SO HARD AND GOT SO FAR')

            time.sleep(0.2)

            l_counter += 1

        expected_image_container = \
            driver.find_elements(By.CSS_SELECTOR, 'div.JT3_zV.z-pdp__escape-grid')
        expected_image_container_list = \
            expected_image_container[0].find_elements(By.CSS_SELECTOR,
                                                      'ul.XLgdq7._0xLoFW.JgpeIw.r9BRio.be4rWJ.xlsKrm._4oK5GO.heWLCX._MmCDa')
        expected_images = \
            expected_image_container_list[0].find_elements(By.CSS_SELECTOR, 'li')

        for image_li in expected_images:
            expected_image = image_li.find_elements(By.CSS_SELECTOR, 'img')
            if len(expected_image) > 0:
                image_link = expected_image[0].get_attribute('src')
                images.append(image_link)
            else:
                print('LIST WITHOUT IMAGE')

    return images


def img_scroll_down(driver):
    scroll_button = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Scroll naar beneden"]')

    if len(scroll_button) > 0:
        scroll_button[0].click()
        time.sleep(0.2)
